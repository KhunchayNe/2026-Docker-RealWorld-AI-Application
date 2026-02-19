# services/qdrant_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct, Distance, VectorParams, 
    Filter, FieldCondition, MatchValue
)
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6333,
        collection_name: str = "oil_prices_eppo"
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        self.vector_size = 384
        
        self._ensure_collection()
    
    def _ensure_collection(self):
        """สร้าง collection ถ้ายังไม่มี"""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, 
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}'")
    
    def add_price_data(self, df: pd.DataFrame) -> int:
        """เพิ่มข้อมูลราคาเข้า Qdrant"""
        points = []
        
        for idx, row in df.iterrows():
            # สร้าง text description
            text_parts = [f"วันที่ {row['date'].strftime('%Y-%m-%d')}"]
            
            if 'diesel' in row and pd.notna(row['diesel']):
                text_parts.append(f"ดีเซล {row['diesel']:.2f} บาท")
            if 'gasohol_95' in row and pd.notna(row['gasohol_95']):
                text_parts.append(f"แก๊สโซฮอล์ 95 {row['gasohol_95']:.2f} บาท")
            
            text = ", ".join(text_parts)
            
            # สร้าง embedding
            vector = self.embedding_model.encode(text).tolist()
            
            # สร้าง payload
            payload = {
                "date": row['date'].isoformat(),
                "diesel": float(row.get('diesel', 0)) if pd.notna(row.get('diesel')) else None,
                "gasohol_95": float(row.get('gasohol_95', 0)) if pd.notna(row.get('gasohol_95')) else None,
                "gasohol_91": float(row.get('gasohol_91', 0)) if pd.notna(row.get('gasohol_91')) else None,
                "gasohol_e20": float(row.get('gasohol_e20', 0)) if pd.notna(row.get('gasohol_e20')) else None,
                "diesel_b7": float(row.get('diesel_b7', 0)) if pd.notna(row.get('diesel_b7')) else None,
                "lpg": float(row.get('lpg', 0)) if pd.notna(row.get('lpg')) else None,
                "day_of_week": int(row['date'].dayofweek),
                "month": int(row['date'].month),
                "year": int(row['date'].year)
            }
            
            points.append(
                PointStruct(
                    id=int(idx),
                    vector=vector,
                    payload=payload
                )
            )
        
        # Batch upsert
        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i:i+batch_size]
            )
        
        logger.info(f"Added {len(points)} records to Qdrant")
        return len(points)
    
    def get_all_prices(self, fuel_type: str = "diesel", limit: int = 10000) -> pd.DataFrame:
        """ดึงข้อมูลราคาทั้งหมด"""
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True
        )
        
        data = []
        for point in results:
            if point.payload.get(fuel_type) is not None:
                data.append({
                    'date': pd.to_datetime(point.payload['date']),
                    fuel_type: point.payload[fuel_type]
                })
        
        df = pd.DataFrame(data)
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def search_similar_prices(
        self, 
        price: float, 
        fuel_type: str = "diesel", 
        limit: int = 5
    ) -> list:
        """
        ค้นหาวันที่มีราคาใกล้เคียง
        ใช้ scroll แทน search เพราะ Qdrant client version ใหม่เปลี่ยน API
        """
        try:
            # ใช้ scroll ดึงข้อมูลทั้งหมดแล้ว filter เอง
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True
            )
            
            similar_dates = []
            for point in results:
                if point.payload.get(fuel_type) is not None:
                    point_price = point.payload[fuel_type]
                    price_diff = abs(point_price - price)
                    similar_dates.append({
                        "date": point.payload['date'],
                        "price": float(point_price),
                        "price_difference": round(price_diff, 2),
                        "similarity_score": 1.0 / (1.0 + price_diff)  # แปลง diff เป็น similarity score
                    })
            
            # Sort by price difference และเอาแค่ limit records
            similar_dates = sorted(similar_dates, key=lambda x: x['price_difference'])[:limit]
            
            return similar_dates
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def store_model_metadata(self, fuel_type: str, metadata: Dict):
        """
        เก็บ model metadata ลง Qdrant collection แยก
        สำหรับ track ประวัติการ train model
        """
        try:
            # ใช้ collection แยกสำหรับ model metadata
            metadata_collection = f"{self.collection_name}_models"

            # สร้าง collection ถ้ายังไม่มี
            try:
                self.client.get_collection(metadata_collection)
            except:
                self.client.create_collection(
                    collection_name=metadata_collection,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created metadata collection '{metadata_collection}'")

            # สร้าง embedding จาก metadata description
            text = f"Model for {fuel_type}, trained on {metadata.get('last_train_date')}, type {metadata.get('model_type')}"
            vector = self.embedding_model.encode(text).tolist()

            # สร้าง point ID จาก fuel_type + timestamp
            point_id = hash(f"{fuel_type}_{metadata.get('created_at', '')}") % (10**10)

            # เพิ่ม metadata ลง collection
            self.client.upsert(
                collection_name=metadata_collection,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=metadata
                    )
                ]
            )

            logger.info(f"Stored model metadata for {fuel_type} in Qdrant (point_id: {point_id})")
            return point_id

        except Exception as e:
            logger.error(f"Failed to store model metadata: {e}")
            raise
