"""
Model Utilities

Helper functions for machine learning model development including:
- Feature engineering and encoding
- Data preprocessing and scaling
- Model persistence (save/load)
- Evaluation metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import pickle
import joblib
import json
from datetime import datetime
from pathlib import Path
import logging

from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import classification_report, confusion_matrix

from utils.logging_utils import get_logger

logger = get_logger(__name__)


def prepare_features(
    df: pd.DataFrame,
    target_column: str,
    categorical_features: Optional[List[str]] = None,
    numerical_features: Optional[List[str]] = None,
    date_features: Optional[List[str]] = None,
    drop_columns: Optional[List[str]] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Dict[str, Any]]:
    """
    Prepare features for machine learning including encoding and scaling.
    
    Args:
        df: Input DataFrame
        target_column: Name of the target variable
        categorical_features: List of categorical column names
        numerical_features: List of numerical column names
        date_features: List of date column names for feature extraction
        drop_columns: Columns to drop
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, encoders)
    """
    logger.info(f"Preparing features for {len(df)} records")
    
    # Make a copy
    data = df.copy()
    
    # Drop specified columns
    if drop_columns:
        data = data.drop(columns=drop_columns, errors='ignore')
    
    # Extract date features
    if date_features:
        data = extract_date_features(data, date_features)
    
    # Separate features and target
    if target_column not in data.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame")
    
    y = data[target_column]
    X = data.drop(columns=[target_column])
    
    # Handle missing values
    X = handle_missing_values(X, categorical_features, numerical_features)
    
    # Encode categorical features
    encoders = {}
    if categorical_features:
        X, encoders = encode_categorical_features(X, categorical_features)
    
    # Scale numerical features
    scaler = None
    if numerical_features:
        X, scaler = scale_numerical_features(X, numerical_features)
        encoders['scaler'] = scaler
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    logger.info(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    
    return X_train, X_test, y_train, y_test, encoders


def extract_date_features(df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
    """
    Extract useful features from date columns.
    
    Args:
        df: Input DataFrame
        date_columns: List of date column names
        
    Returns:
        DataFrame with extracted date features
    """
    data = df.copy()
    
    for col in date_columns:
        if col not in data.columns:
            continue
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(data[col]):
            data[col] = pd.to_datetime(data[col], errors='coerce')
        
        # Extract features
        data[f'{col}_year'] = data[col].dt.year
        data[f'{col}_month'] = data[col].dt.month
        data[f'{col}_day'] = data[col].dt.day
        data[f'{col}_dayofweek'] = data[col].dt.dayofweek
        data[f'{col}_quarter'] = data[col].dt.quarter
        
        # Calculate days since epoch (for relative time)
        data[f'{col}_days_since_epoch'] = (
            pd.to_datetime(data[col]) - pd.Timestamp('1970-01-01')
        ).dt.days  # type: ignore
        
        # Drop original date column
        data = data.drop(columns=[col])
    
    logger.info(f"Extracted date features from {len(date_columns)} columns")
    return data


def handle_missing_values(
    df: pd.DataFrame,
    categorical_features: Optional[List[str]] = None,
    numerical_features: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: Input DataFrame
        categorical_features: List of categorical columns
        numerical_features: List of numerical columns
        
    Returns:
        DataFrame with handled missing values
    """
    data = df.copy()
    
    # Fill categorical missing values with 'unknown'
    if categorical_features:
        for col in categorical_features:
            if col in data.columns:
                data[col] = data[col].fillna('unknown')
    
    # Fill numerical missing values with median
    if numerical_features:
        for col in numerical_features:
            if col in data.columns:
                median_val = data[col].median()
                data[col] = data[col].fillna(median_val)
    
    return data


def encode_categorical_features(
    df: pd.DataFrame,
    categorical_features: List[str],
    encoding_type: str = 'label'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Encode categorical features.
    
    Args:
        df: Input DataFrame
        categorical_features: List of categorical column names
        encoding_type: 'label' or 'onehot'
        
    Returns:
        Tuple of (encoded DataFrame, encoder dictionary)
    """
    data = df.copy()
    encoders = {}
    
    if encoding_type == 'label':
        for col in categorical_features:
            if col not in data.columns:
                continue
            
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col].astype(str))
            encoders[col] = le
    
    elif encoding_type == 'onehot':
        # Use pandas get_dummies for simplicity
        data = pd.get_dummies(data, columns=categorical_features, drop_first=True)
        encoders['onehot_columns'] = [col for col in data.columns if any(cat in col for cat in categorical_features)]
    
    logger.info(f"Encoded {len(categorical_features)} categorical features using {encoding_type} encoding")
    return data, encoders


def scale_numerical_features(
    df: pd.DataFrame,
    numerical_features: List[str]
) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Scale numerical features using StandardScaler.
    
    Args:
        df: Input DataFrame
        numerical_features: List of numerical column names
        
    Returns:
        Tuple of (scaled DataFrame, fitted scaler)
    """
    data = df.copy()
    scaler = StandardScaler()
    
    # Get only the columns that exist in the DataFrame
    existing_features = [col for col in numerical_features if col in data.columns]
    
    if existing_features:
        data[existing_features] = scaler.fit_transform(data[existing_features])
        logger.info(f"Scaled {len(existing_features)} numerical features")
    
    return data, scaler


def save_model(
    model: Any,
    model_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Save a trained model to disk.
    
    Args:
        model: Trained model object
        model_path: Path to save the model
        metadata: Optional metadata dictionary
    """
    logger.info(f"Saving model to {model_path}")
    
    try:
        # Create directory if it doesn't exist
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model using joblib (better for sklearn models)
        joblib.dump(model, model_path)
        
        # Save metadata if provided
        if metadata:
            metadata_path = model_path.replace('.pkl', '_metadata.json')
            with open(metadata_path, 'w') as f:
                # Convert any datetime objects to strings
                metadata_serializable = {
                    k: str(v) if isinstance(v, datetime) else v
                    for k, v in metadata.items()
                }
                json.dump(metadata_serializable, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}")
        
        logger.info("Model saved successfully")
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}", exc_info=True)
        raise


def load_model(model_path: str) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Load a trained model from disk.
    
    Args:
        model_path: Path to the saved model
        
    Returns:
        Tuple of (model object, metadata dictionary)
    """
    logger.info(f"Loading model from {model_path}")
    
    try:
        # Load model
        model = joblib.load(model_path)
        
        # Load metadata if exists
        metadata = None
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            logger.info("Loaded metadata")
        
        logger.info("Model loaded successfully")
        return model, metadata
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}", exc_info=True)
        raise


def evaluate_regression_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, float]:
    """
    Evaluate regression model performance.
    
    Args:
        y_true: True target values
        y_pred: Predicted target values
        model_name: Name of the model for logging
        
    Returns:
        Dictionary of evaluation metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    # Mean Absolute Percentage Error (handle divide by zero)
    mape = np.mean(np.abs((y_true - y_pred) / np.where(y_true != 0, y_true, 1))) * 100
    
    metrics = {
        'mae': round(mae, 2),
        'mse': round(mse, 2),
        'rmse': round(rmse, 2),
        'r2': round(r2, 4),
        'mape': round(mape, 2)
    }
    
    logger.info(f"{model_name} Evaluation Metrics:")
    for metric, value in metrics.items():
        logger.info(f"  {metric.upper()}: {value}")
    
    return metrics


def evaluate_classification_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, Any]:
    """
    Evaluate classification model performance.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        model_name: Name of the model for logging
        
    Returns:
        Dictionary of evaluation metrics
    """
    # Get classification report as dict
    report = classification_report(y_true, y_pred, output_dict=True)
    
    # Get confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'accuracy': round(float(report.get('accuracy', 0.0)), 4)  # type: ignore
    }
    
    logger.info(f"{model_name} Evaluation Metrics:")
    logger.info(f"  Accuracy: {metrics['accuracy']}")
    logger.info(f"\nClassification Report:\n{classification_report(y_true, y_pred)}")
    
    return metrics


def create_feature_importance_df(
    model: Any,
    feature_names: List[str],
    top_n: int = 20
) -> pd.DataFrame:
    """
    Create a DataFrame of feature importances from a tree-based model.
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        DataFrame with feature importances
    """
    if not hasattr(model, 'feature_importances_'):
        logger.warning("Model does not have feature_importances_ attribute")
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(top_n)
    
    logger.info(f"Created feature importance DataFrame with top {top_n} features")
    return importance_df


def generate_model_report(
    metrics: Dict[str, Any],
    model_name: str,
    model_type: str = "regression"
) -> str:
    """
    Generate a Markdown report for model performance.
    
    Args:
        metrics: Dictionary of evaluation metrics
        model_name: Name of the model
        model_type: Type of model ('regression' or 'classification')
        
    Returns:
        Markdown-formatted report
    """
    report = []
    report.append(f"# {model_name} Performance Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Model Type:** {model_type.capitalize()}\n\n")
    
    if model_type == "regression":
        report.append("## Regression Metrics\n")
        report.append(f"- **Mean Absolute Error (MAE):** {metrics.get('mae', 'N/A')}\n")
        report.append(f"- **Root Mean Squared Error (RMSE):** {metrics.get('rmse', 'N/A')}\n")
        report.append(f"- **R² Score:** {metrics.get('r2', 'N/A')}\n")
        report.append(f"- **Mean Absolute Percentage Error (MAPE):** {metrics.get('mape', 'N/A')}%\n")
    
    elif model_type == "classification":
        report.append("## Classification Metrics\n")
        report.append(f"- **Accuracy:** {metrics.get('accuracy', 'N/A')}\n")
        
        if 'classification_report' in metrics:
            report.append("\n### Detailed Classification Report\n")
            report.append("```\n")
            # Format classification report
            cr = metrics['classification_report']
            for key, values in cr.items():
                if isinstance(values, dict):
                    report.append(f"{key}:\n")
                    for metric, value in values.items():
                        report.append(f"  {metric}: {value:.4f}\n")
            report.append("```\n")
    
    return ''.join(report)


if __name__ == "__main__":
    # Example usage
    logger.info("Model utilities module loaded successfully")
