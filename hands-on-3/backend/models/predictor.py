# models/predictor.py
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import os
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class OilPricePredictor:
    """
    Time series predictor ใช้ SARIMA model
    """
    
    def __init__(self, model_dir: str = "./models", qdrant_service=None):
        self.model_dir = model_dir
        self.model = None
        self.model_fit = None
        self.scaler = None
        self.fuel_type = None
        self.last_train_date = None
        self.qdrant_service = qdrant_service

        os.makedirs(model_dir, exist_ok=True)
    
    def train(
        self, 
        df: pd.DataFrame, 
        fuel_type: str = "diesel",
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 7)
    ) -> Dict[str, float]:
        """
        Train SARIMA model
        
        Args:
            df: DataFrame with 'date' and fuel_type columns
            fuel_type: ประเภทเชื้อเพลิง
            order: (p, d, q) for ARIMA
            seasonal_order: (P, D, Q, s) for seasonal component
        """
        self.fuel_type = fuel_type
        
        # เตรียมข้อมูล
        df = df.sort_values('date').copy()
        ts = df.set_index('date')[fuel_type]
        
        # ลบ missing values
        ts = ts.dropna()
        
        if len(ts) < 30:
            raise ValueError(f"Not enough data: {len(ts)} records. Need at least 30.")
        
        logger.info(f"Training with {len(ts)} records from {ts.index.min()} to {ts.index.max()}")
        
        try:
            # Train SARIMA
            self.model = SARIMAX(
                ts,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            self.model_fit = self.model.fit(disp=False, maxiter=200)
            self.last_train_date = ts.index.max()
            
            # Calculate metrics
            predictions = self.model_fit.fittedvalues
            residuals = ts - predictions
            
            mae = np.mean(np.abs(residuals))
            rmse = np.sqrt(np.mean(residuals**2))
            mape = np.mean(np.abs(residuals / ts)) * 100
            
            metrics = {
                "mae": float(mae),
                "rmse": float(rmse),
                "mape": float(mape),
                "aic": float(self.model_fit.aic),
                "bic": float(self.model_fit.bic)
            }
            
            # Save model
            self.save_model()
            
            logger.info(f"Training completed. MAE: {mae:.3f}, RMSE: {rmse:.3f}, MAPE: {mape:.2f}%")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            
            # Fallback to Exponential Smoothing
            logger.info("Falling back to Exponential Smoothing...")
            self.model = ExponentialSmoothing(
                ts, 
                seasonal_periods=7, 
                trend='add', 
                seasonal='add'
            )
            self.model_fit = self.model.fit()
            self.last_train_date = ts.index.max()
            
            predictions = self.model_fit.fittedvalues
            residuals = ts - predictions
            mae = np.mean(np.abs(residuals))
            
            self.save_model()
            
            return {"mae": float(mae), "model": "ExponentialSmoothing"}
    
    def predict(self, periods: int = 7, confidence: float = 0.95) -> List[Dict]:
        """
        ทำนายราคา N วันข้างหน้า
        
        Args:
            periods: จำนวนวันที่ต้องการทำนาย
            confidence: confidence level สำหรับ interval
        """
        if self.model_fit is None:
            raise ValueError("Model not trained. Call train() first.")
        
        try:
            # SARIMA forecast
            if hasattr(self.model_fit, 'get_forecast'):
                forecast_result = self.model_fit.get_forecast(steps=periods)
                forecast = forecast_result.predicted_mean
                conf_int = forecast_result.conf_int(alpha=1-confidence)
                
                predictions = []
                for i in range(periods):
                    pred_date = self.last_train_date + pd.Timedelta(days=i+1)
                    predictions.append({
                        'day': i + 1,
                        'date': pred_date.strftime("%Y-%m-%d"),
                        'predicted_price': round(float(forecast.iloc[i]), 2),
                        'lower_bound': round(float(conf_int.iloc[i, 0]), 2),
                        'upper_bound': round(float(conf_int.iloc[i, 1]), 2)
                    })
            else:
                # Exponential Smoothing
                forecast = self.model_fit.forecast(periods)
                predictions = []
                for i in range(periods):
                    pred_date = self.last_train_date + pd.Timedelta(days=i+1)
                    pred_value = float(forecast[i])
                    # ประมาณ confidence interval (±2%)
                    predictions.append({
                        'day': i + 1,
                        'date': pred_date.strftime("%Y-%m-%d"),
                        'predicted_price': round(pred_value, 2),
                        'lower_bound': round(pred_value * 0.98, 2),
                        'upper_bound': round(pred_value * 1.02, 2)
                    })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def save_model(self):
        """บันทึก model metadata ลง Qdrant และ save model file local"""
        if self.model_fit is None:
            return

        # Save model metadata to Qdrant
        model_metadata = {
            'fuel_type': self.fuel_type,
            'last_train_date': self.last_train_date.strftime("%Y-%m-%d") if hasattr(self.last_train_date, 'strftime') else str(self.last_train_date),
            'model_type': 'SARIMA' if hasattr(self.model_fit, 'get_forecast') else 'ExponentialSmoothing',
            'created_at': pd.Timestamp.now().isoformat()
        }

        # Store in Qdrant for tracking
        if self.qdrant_service:
            try:
                self.qdrant_service.store_model_metadata(self.fuel_type, model_metadata)
                logger.info(f"Model metadata stored in Qdrant for {self.fuel_type}")
            except Exception as e:
                logger.warning(f"Could not store metadata in Qdrant: {e}")
        else:
            logger.info("No qdrant_service provided, skipping metadata storage")

        # Save actual model to local filesystem (SARIMA models are too large for Qdrant)
        model_path = os.path.join(self.model_dir, f"{self.fuel_type}_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model_fit': self.model_fit,
                'fuel_type': self.fuel_type,
                'last_train_date': self.last_train_date,
                'metadata': model_metadata
            }, f)

        logger.info(f"Model saved to {model_path}")

    def load_model(self, fuel_type: str):
        """โหลด model จาก local file"""
        model_path = os.path.join(self.model_dir, f"{fuel_type}_model.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model for {fuel_type} not found at {model_path}")

        with open(model_path, 'rb') as f:
            data = pickle.load(f)

        self.model_fit = data['model_fit']
        self.fuel_type = data['fuel_type']
        self.last_train_date = data['last_train_date']

        logger.info(f"Model loaded from {model_path}")

    def model_exists(self, fuel_type: str) -> bool:
        """ตรวจสอบว่ามี model สำหรับ fuel_type นี้หรือไม่"""
        model_path = os.path.join(self.model_dir, f"{fuel_type}_model.pkl")
        return os.path.exists(model_path)
