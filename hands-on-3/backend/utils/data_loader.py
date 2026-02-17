# utils/data_loader.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_eppo_csv(file_path: str, encoding: str = 'utf-8-sig') -> pd.DataFrame:
    """
    โหลดข้อมูลจาก EPPO CSV
    รองรับหลายรูปแบบ encoding และ column names
    """
    try:
        # ลองหลาย encoding
        for enc in [encoding, 'utf-8', 'tis-620', 'cp874']:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                logger.info(f"Successfully loaded with encoding: {enc}")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Cannot decode CSV file")
        
        # แสดง columns ที่มี
        logger.info(f"Columns found: {df.columns.tolist()}")
        
        # Normalize column names
        df.columns = df.columns.str.strip()
        
        # แปลง date column
        date_cols = ['date', 'Date', 'วันที่', 'ว/ด/ป']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            df['date'] = pd.to_datetime(df[date_col], errors='coerce')
            logger.info(f"Date column detected: {date_col}")
        else:
            logger.warning("No date column found, using index")
            df['date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='D')
        
        # Normalize price column names
        column_mapping = {
            'ดีเซล': 'diesel',
            'Diesel': 'diesel',
            'แก๊สโซฮอล์ 95': 'gasohol_95',
            'Gasohol 95': 'gasohol_95',
            'แก๊สโซฮอล์ 91': 'gasohol_91',
            'Gasohol 91': 'gasohol_91',
            'E20': 'gasohol_e20',
            'แก๊สโซฮอล์ E20': 'gasohol_e20',
            'ดีเซล B7': 'diesel_b7',
            'Diesel B7': 'diesel_b7',
            'ก๊าซ LPG': 'lpg',
            'LPG': 'lpg'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clean price columns
        price_columns = ['diesel', 'gasohol_95', 'gasohol_91', 
                        'gasohol_e20', 'diesel_b7', 'lpg']
        
        for col in price_columns:
            if col in df.columns:
                # ลบ comma และแปลงเป็น float
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('-', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # เรียงตามวันที่
        df = df.sort_values('date').reset_index(drop=True)
        
        # เติมค่าว่างด้วย forward fill
        # df = df.fillna(method='ffill').fillna(method='bfill')
        df = df.ffill().bfill()
                
        # ลบ rows ที่ date เป็น NaT
        df = df.dropna(subset=['date'])
        
        logger.info(f"Loaded {len(df)} records from {df['date'].min()} to {df['date'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise

def create_features(df: pd.DataFrame, target_col: str = 'diesel') -> pd.DataFrame:
    """
    สร้าง features สำหรับ time series forecasting
    """
    df = df.copy()
    
    if target_col not in df.columns:
        raise ValueError(f"Column {target_col} not found in dataframe")
    
    # Time-based features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    df['day_of_month'] = df['date'].dt.day
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Lag features
    for lag in [1, 2, 3, 7, 14, 30]:
        df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
    
    # Rolling statistics
    for window in [3, 7, 14, 30]:
        df[f'{target_col}_ma_{window}'] = df[target_col].rolling(window=window).mean()
        df[f'{target_col}_std_{window}'] = df[target_col].rolling(window=window).std()
        df[f'{target_col}_min_{window}'] = df[target_col].rolling(window=window).min()
        df[f'{target_col}_max_{window}'] = df[target_col].rolling(window=window).max()
    
    # Price changes
    df[f'{target_col}_pct_change'] = df[target_col].pct_change()
    df[f'{target_col}_diff'] = df[target_col].diff()
    
    # ลบ NaN rows
    df = df.dropna()
    
    return df

def prepare_sample_data() -> pd.DataFrame:
    """
    สร้างข้อมูลตัวอย่างสำหรับทดสอบ
    """
    dates = pd.date_range(start='2024-01-01', end='2026-02-17', freq='D')
    
    # สร้างราคาจำลองที่มี trend และ seasonality
    np.random.seed(42)
    trend = np.linspace(30, 35, len(dates))
    seasonal = 2 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    noise = np.random.normal(0, 0.5, len(dates))
    
    diesel_price = trend + seasonal + noise
    gasohol_95_price = diesel_price + 8 + np.random.normal(0, 0.3, len(dates))
    gasohol_91_price = diesel_price + 6 + np.random.normal(0, 0.3, len(dates))
    
    df = pd.DataFrame({
        'date': dates,
        'diesel': diesel_price,
        'gasohol_95': gasohol_95_price,
        'gasohol_91': gasohol_91_price,
        'lpg': 20 + np.random.normal(0, 0.5, len(dates))
    })
    
    return df
