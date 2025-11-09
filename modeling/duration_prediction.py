"""
Case Duration Prediction Model

Machine learning model to predict expected case duration based on:
- Case type
- Court characteristics  
- Filing date
- Historical patterns
- Adjournment history
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from sqlalchemy.orm import Session

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
import xgboost as xgb

from models.data_models import Case, Court, Hearing
from modeling.model_utils import (
    prepare_features, save_model, load_model,
    evaluate_regression_model, create_feature_importance_df,
    generate_model_report
)
from utils.logging_utils import get_logger
from utils.db_utils import get_db_session

logger = get_logger(__name__)


class CaseDurationPredictor:
    """
    Predict expected case duration using machine learning.
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the predictor.
        
        Args:
            model_type: Type of model ('linear', 'random_forest', 'gradient_boosting', 'xgboost')
        """
        self.model_type = model_type
        self.model = None
        self.encoders = None
        self.feature_names = None
        
        # Initialize model based on type
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'xgboost':
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        logger.info(f"Initialized CaseDurationPredictor with {model_type} model")
    
    def prepare_training_data(
        self,
        db_session: Optional[Session] = None
    ) -> pd.DataFrame:
        """
        Prepare training data from disposed cases.
        
        Args:
            db_session: Database session
            
        Returns:
            DataFrame with features and target
        """
        logger.info("Preparing training data from disposed cases")
        
        close_session = False
        if db_session is None:
            db_session = get_db_session()
            close_session = True
        
        try:
            # Query disposed cases with duration
            from sqlalchemy import func
            
            query = db_session.query(
                Case.case_id,
                Case.case_type,
                Case.filing_date,
                Case.disposal_date,
                Court.court_code,
                Court.court_type,
                Court.state,
                func.count(Hearing.hearing_id).label('hearing_count'),
                func.extract('days', Case.disposal_date - Case.filing_date).label('duration_days')
            ).join(Court, Case.court_id == Court.court_id
            ).outerjoin(Hearing, Case.case_id == Hearing.case_id
            ).filter(
                Case.disposal_date.isnot(None),
                Case.filing_date.isnot(None)
            ).group_by(
                Case.case_id,
                Case.case_type,
                Case.filing_date,
                Case.disposal_date,
                Court.court_code,
                Court.court_type,
                Court.state
            )
            
            results = query.all()
            
            if not results:
                logger.warning("No disposed cases found for training")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'case_id': r.case_id,
                    'case_type': r.case_type.value if r.case_type else 'unknown',
                    'filing_date': r.filing_date,
                    'court_code': r.court_code,
                    'court_type': r.court_type,
                    'state': r.state,
                    'hearing_count': r.hearing_count,
                    'duration_days': float(r.duration_days) if r.duration_days else None
                }
                for r in results
            ])
            
            # Filter out invalid durations
            df = df[df['duration_days'] > 0]
            df = df[df['duration_days'] < 3650]  # Less than 10 years
            
            logger.info(f"Prepared {len(df)} training samples")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}", exc_info=True)
            raise
        finally:
            if close_session:
                db_session.close()
    
    def train(
        self,
        training_data: pd.DataFrame,
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Train the duration prediction model.
        
        Args:
            training_data: DataFrame with features and target
            test_size: Proportion for test set
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Training {self.model_type} model on {len(training_data)} samples")
        
        # Define feature columns
        categorical_features = ['case_type', 'court_code', 'court_type', 'state']
        numerical_features = ['hearing_count']
        date_features = ['filing_date']
        drop_columns = ['case_id']
        target_column = 'duration_days'
        
        # Prepare features
        X_train, X_test, y_train, y_test, encoders = prepare_features(
            training_data,
            target_column=target_column,
            categorical_features=categorical_features,
            numerical_features=numerical_features,
            date_features=date_features,
            drop_columns=drop_columns,
            test_size=test_size
        )
        
        # Store encoders and feature names
        self.encoders = encoders
        self.feature_names = X_train.columns.tolist()
        
        # Train model
        logger.info("Training model...")
        self.model.fit(X_train, y_train)  # type: ignore
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test)  # type: ignore
        metrics = evaluate_regression_model(
            y_test.to_numpy(), y_pred, self.model_type  # type: ignore
        )
        
        # Cross-validation score
        cv_scores = cross_val_score(
            self.model, X_train, y_train,  # type: ignore
            cv=5, scoring='neg_mean_absolute_error'
        )
        metrics['cv_mae'] = round(-cv_scores.mean(), 2)
        logger.info(f"Cross-validation MAE: {metrics['cv_mae']}")
        
        return metrics
    
    def predict(self, case_data: pd.DataFrame) -> np.ndarray:
        """
        Predict case duration for new cases.
        
        Args:
            case_data: DataFrame with case features
            
        Returns:
            Array of predicted durations in days
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info(f"Predicting duration for {len(case_data)} cases")
        
        # Prepare features (apply same transformations as training)
        # This would need the same encoding/scaling logic
        # For simplicity, assuming data is already prepared
        
        predictions = self.model.predict(case_data)
        return np.maximum(predictions, 0)  # Ensure non-negative
    
    def get_feature_importance(self, top_n: int = 15) -> pd.DataFrame:
        """
        Get feature importance from tree-based models.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importances
        """
        if self.feature_names is None:
            logger.warning("No feature names available")
            return pd.DataFrame()
        
        return create_feature_importance_df(self.model, self.feature_names, top_n)
    
    def save(self, model_path: str = "modeling/models/duration_predictor.pkl") -> None:
        """
        Save the trained model.
        
        Args:
            model_path: Path to save the model
        """
        metadata = {
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }
        save_model(self.model, model_path, metadata)
        
        # Save encoders separately
        encoder_path = model_path.replace('.pkl', '_encoders.pkl')
        save_model(self.encoders, encoder_path)
        
        logger.info(f"Model and encoders saved")
    
    def load(self, model_path: str = "modeling/models/duration_predictor.pkl") -> None:
        """
        Load a trained model.
        
        Args:
            model_path: Path to the saved model
        """
        self.model, metadata = load_model(model_path)
        
        # Load encoders
        encoder_path = model_path.replace('.pkl', '_encoders.pkl')
        self.encoders, _ = load_model(encoder_path)
        
        if metadata:
            self.model_type = metadata.get('model_type', 'unknown')
            self.feature_names = metadata.get('feature_names', [])
        
        logger.info(f"Loaded {self.model_type} model")


def train_and_evaluate_models(
    db_session: Optional[Session] = None
) -> Dict[str, Dict[str, float]]:
    """
    Train and compare multiple model types.
    
    Args:
        db_session: Database session
        
    Returns:
        Dictionary of metrics for each model type
    """
    logger.info("Training and comparing multiple models")
    
    # Initialize predictor to get training data
    temp_predictor = CaseDurationPredictor()
    training_data = temp_predictor.prepare_training_data(db_session)
    
    if training_data.empty:
        logger.error("No training data available")
        return {}
    
    # Model types to compare
    model_types = ['linear', 'random_forest', 'gradient_boosting', 'xgboost']
    results = {}
    
    for model_type in model_types:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Training {model_type} model")
            logger.info(f"{'='*60}")
            
            predictor = CaseDurationPredictor(model_type=model_type)
            metrics = predictor.train(training_data)
            results[model_type] = metrics
            
            # Save the model
            predictor.save(f"modeling/models/duration_{model_type}.pkl")
            
        except Exception as e:
            logger.error(f"Error training {model_type}: {str(e)}")
            results[model_type] = {'error': str(e)}
    
    # Identify best model
    best_model = min(results.items(), key=lambda x: x[1].get('mae', float('inf')))
    logger.info(f"\nBest Model: {best_model[0]} (MAE: {best_model[1]['mae']})")
    
    return results


def generate_duration_report(
    model_results: Dict[str, Dict[str, float]],
    output_path: str = "reports/MODEL_METRICS.md"
) -> None:
    """
    Generate a comprehensive model performance report.
    
    Args:
        model_results: Dictionary of results from each model
        output_path: Path to save the report
    """
    logger.info(f"Generating model report at {output_path}")
    
    report = []
    report.append("# Case Duration Prediction Model Report\n\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    report.append("## Model Comparison\n\n")
    report.append("| Model Type | MAE (days) | RMSE (days) | R² Score | CV MAE |\n")
    report.append("|------------|-----------|-------------|----------|--------|\n")
    
    for model_type, metrics in model_results.items():
        if 'error' in metrics:
            report.append(f"| {model_type} | ERROR | - | - | - |\n")
        else:
            report.append(
                f"| {model_type} | {metrics.get('mae', 'N/A')} | "
                f"{metrics.get('rmse', 'N/A')} | {metrics.get('r2', 'N/A')} | "
                f"{metrics.get('cv_mae', 'N/A')} |\n"
            )
    
    # Best model
    valid_results = {k: v for k, v in model_results.items() if 'error' not in v}
    if valid_results:
        best_model = min(valid_results.items(), key=lambda x: x[1]['mae'])
        report.append(f"\n## Best Performing Model\n\n")
        report.append(f"**{best_model[0]}** achieved the lowest MAE of **{best_model[1]['mae']} days**.\n\n")
        
        report.append("### Interpretation\n\n")
        report.append(f"- The model can predict case duration with an average error of {best_model[1]['mae']} days.\n")
        report.append(f"- R² score of {best_model[1]['r2']} indicates the model explains "
                     f"{best_model[1]['r2']*100:.1f}% of the variance in case duration.\n")
    
    # Write report
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    logger.info(f"Report saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    logger.info("Training case duration prediction models")
    
    # Train and compare models
    results = train_and_evaluate_models()
    
    # Generate report
    if results:
        generate_duration_report(results)
        print("\n✓ Model training complete. Report saved to reports/MODEL_METRICS.md")
