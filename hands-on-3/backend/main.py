# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
import pandas as pd
import logging
import os
from datetime import datetime
from typing import Optional

from schemas.price_schemas import (
    PriceData, PredictionRequest, PredictionResponse,
    TrainingRequest, UploadResponse, PredictionResult
)
from services.qdrant_service import QdrantService
from models.predictor import OilPricePredictor
from utils.data_loader import load_eppo_csv, prepare_sample_data

# Configuration
class Settings(BaseSettings):
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "oil_prices_eppo"
    model_dir: str = "./models"
    data_dir: str = "./data"

    class Config:
        env_file = ".env"

settings = Settings()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Oil Price Prediction API",
    description="API สำหรับทำนายราคาน้ำมันด้วย Machine Learning + Qdrant Vector DB",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1,
        "docExpansion": "list"
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qdrant_service = QdrantService(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    collection_name=settings.collection_name
)

predictor = OilPricePredictor(model_dir=settings.model_dir, qdrant_service=qdrant_service)

# Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "service": "Oil Price Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "upload": "/upload-csv",
            "add_price": "/prices",
            "train": "/train",
            "predict": "/predict",
            "search": "/search"
        }
    }

@app.get("/health")
async def health_check():
    """ตรวจสอบสถานะของ services"""
    try:
        # Check Qdrant
        collections = qdrant_service.client.get_collections()
        qdrant_status = "connected"
    except:
        qdrant_status = "disconnected"
    
    return {
        "status": "healthy",
        "qdrant": qdrant_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload-csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    อัพโหลด CSV จาก EPPO
    """
    try:
        # Save uploaded file
        file_path = os.path.join(settings.data_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Load and process
        df = load_eppo_csv(file_path)
        
        # Add to Qdrant
        records_added = qdrant_service.add_price_data(df)
        
        return UploadResponse(
            status="success",
            records_added=records_added,
            date_range={
                "start": df['date'].min().strftime("%Y-%m-%d"),
                "end": df['date'].max().strftime("%Y-%m-%d")
            }
        )
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload-csv-url")
async def upload_csv_from_url(url: str):
    """
    โหลด CSV จาก URL (เช่น EPPO catalog)
    """
    try:
        import requests
        from io import StringIO
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to temp file
        file_path = os.path.join(settings.data_dir, "temp_eppo.csv")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Load and process
        df = load_eppo_csv(file_path)
        
        # Add to Qdrant
        records_added = qdrant_service.add_price_data(df)
        
        return {
            "status": "success",
            "records_added": records_added,
            "date_range": {
                "start": df['date'].min().strftime("%Y-%m-%d"),
                "end": df['date'].max().strftime("%Y-%m-%d")
            }
        }
    
    except Exception as e:
        logger.error(f"URL upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-sample-data")
async def generate_sample_data():
    """
    สร้างข้อมูลตัวอย่างสำหรับทดสอบ
    """
    try:
        df = prepare_sample_data()
        records_added = qdrant_service.add_price_data(df)
        
        return {
            "status": "success",
            "message": "Sample data generated",
            "records_added": records_added,
            "date_range": {
                "start": df['date'].min().strftime("%Y-%m-%d"),
                "end": df['date'].max().strftime("%Y-%m-%d")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prices")
async def add_price(data: PriceData):
    """
    เพิ่มราคาใหม่ทีละรายการ
    """
    try:
        df = pd.DataFrame([{
            'date': pd.to_datetime(data.date),
            'diesel': data.diesel,
            'gasohol_95': data.gasohol_95,
            'gasohol_91': data.gasohol_91,
            'gasohol_e20': data.gasohol_e20,
            'diesel_b7': data.diesel_b7,
            'lpg': data.lpg
        }])
        
        qdrant_service.add_price_data(df)
        
        return {"status": "success", "date": data.date}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Train model สำหรับ fuel_type ที่ระบุ
    """
    try:
        fuel_type = request.fuel_type
        
        # Check if model exists
        if predictor.model_exists(fuel_type) and not request.retrain:
            return {
                "status": "model_exists",
                "message": f"Model for {fuel_type} already exists. Use retrain=true to force retrain.",
                "fuel_type": fuel_type
            }
        
        # Get data from Qdrant
        df = qdrant_service.get_all_prices(fuel_type=fuel_type)
        
        if len(df) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough data: {len(df)} records. Need at least 30."
            )
        
        # Train model
        metrics = predictor.train(df, fuel_type=fuel_type)
        
        return {
            "status": "trained",
            "fuel_type": fuel_type,
            "samples": len(df),
            "metrics": metrics,
            "last_train_date": predictor.last_train_date.strftime("%Y-%m-%d")
        }
    
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
async def predict_price(request: PredictionRequest):
    """
    ทำนายราคาน้ำมัน
    """
    try:
        fuel_type = request.fuel_type
        
        # Load model if not loaded
        if predictor.fuel_type != fuel_type:
            predictor.load_model(fuel_type)
        
        # Get current price
        df = qdrant_service.get_all_prices(fuel_type=fuel_type, limit=1)
        if len(df) == 0:
            raise HTTPException(status_code=404, detail="No price data found")
        
        current_price = float(df[fuel_type].iloc[-1])
        
        # Predict
        predictions = predictor.predict(periods=request.horizon)
        
        prediction_results = [
            PredictionResult(**pred) for pred in predictions
        ]
        
        return PredictionResponse(
            fuel_type=fuel_type,
            current_price=current_price,
            predictions=prediction_results,
            model_info={
                "last_train_date": predictor.last_train_date.strftime("%Y-%m-%d")
            }
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Model for {request.fuel_type} not found. Please train first."
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_similar_prices(
    price: float,
    fuel_type: str = "diesel",
    limit: int = 5
):
    """
    ค้นหาวันที่มีราคาใกล้เคียง
    """
    try:
        results = qdrant_service.search_similar_prices(
            price=price,
            fuel_type=fuel_type,
            limit=limit
        )
        return {"similar_dates": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/latest")
async def get_latest_prices():
    """
    ดึงราคาล่าสุดของทุกประเภท
    """
    try:
        fuel_types = ['diesel', 'gasohol_95', 'gasohol_91', 'lpg']
        latest_prices = {}
        
        for fuel_type in fuel_types:
            try:
                df = qdrant_service.get_all_prices(fuel_type=fuel_type, limit=1)
                if len(df) > 0:
                    latest_prices[fuel_type] = {
                        "price": float(df[fuel_type].iloc[-1]),
                        "date": df['date'].iloc[-1].strftime("%Y-%m-%d")
                    }
            except:
                continue
        
        return {"latest_prices": latest_prices}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
