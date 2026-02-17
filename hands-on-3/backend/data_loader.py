# data_loader.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_eppo_data(csv_path: str):
    """โหลดข้อมูลราคาน้ำมันจาก EPPO"""
    # อ่าน CSV ด้วย encoding ภาษาไทย
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # แปลง column names (ปรับตาม structure จริง)
    # ตัวอย่าง columns: วันที่, แก๊สโซฮอล์ 95, แก๊สโซฮอล์ 91, ดีเซล, ดีเซล B7, ก๊าซ LPG
    
    # Clean และ format วันที่
    if 'วันที่' in df.columns:
        df['date'] = pd.to_datetime(df['วันที่'], errors='coerce')
    
    # แปลงราคาเป็น float (ลบ comma ถ้ามี)
    price_columns = [col for col in df.columns if col not in ['date', 'วันที่']]
    for col in price_columns:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    
    # เรียงตามวันที่
    df = df.sort_values('date').reset_index(drop=True)
    
    # เติมค่าว่าง (forward fill)
    df = df.fillna(method='ffill')
    
    return df

def create_features(df: pd.DataFrame, target_col: str = 'ดีเซล'):
    """สร้าง features สำหรับ ML model"""
    df = df.copy()
    
    # Time-based features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    
    # Lag features (ราคาย้อนหลัง)
    for lag in [1, 2, 7, 14, 30]:
        df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
    
    # Rolling statistics
    for window in [7, 14, 30]:
        df[f'{target_col}_ma_{window}'] = df[target_col].rolling(window).mean()
        df[f'{target_col}_std_{window}'] = df[target_col].rolling(window).std()
    
    # Price change
    df[f'{target_col}_pct_change'] = df[target_col].pct_change()
    
    # ลบ rows ที่มี NaN
    df = df.dropna()
    
    return df
