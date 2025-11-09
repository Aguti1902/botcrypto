"""Feature engineering for ML models."""
import pandas as pd
import numpy as np
import pandas_ta as ta


class FeatureEngineer:
    """Generate ML features from OHLCV data."""
    
    @staticmethod
    def generate_features(df: pd.DataFrame) -> pd.DataFrame:
        """Generate features from OHLCV data.
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            DataFrame with features
        """
        features = df.copy()
        
        # Returns
        features['returns_1'] = features['close'].pct_change(1)
        features['returns_5'] = features['close'].pct_change(5)
        features['returns_20'] = features['close'].pct_change(20)
        
        # Volatility
        features['volatility_20'] = features['returns_1'].rolling(20).std()
        features['atr_14'] = ta.atr(features['high'], features['low'], features['close'], length=14)
        features['atr_norm'] = features['atr_14'] / features['close']
        
        # Technical indicators
        features['rsi_14'] = ta.rsi(features['close'], length=14)
        bbands = ta.bbands(features['close'], length=20)
        features['bb_pct'] = (features['close'] - bbands['BBL_20_2.0']) / (bbands['BBU_20_2.0'] - bbands['BBL_20_2.0'])
        
        # Volume
        features['volume_ratio'] = features['volume'] / features['volume'].rolling(20).mean()
        
        # Z-scores
        features['close_zscore'] = (features['close'] - features['close'].rolling(50).mean()) / features['close'].rolling(50).std()
        
        # Drop NaN
        features = features.dropna()
        
        return features

