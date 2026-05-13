from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import lightgbm as lgb
import numpy as np
import pandas as pd
import os
import io
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Amazon Review Predictor API",
    description="Predicts whether a user will like a product review (≥4 stars)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Model Loading ---
# Use environment variable, fallback to relative path
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "model", "amazon_lgb_model.txt"))

try:
    logger.info(f"Loading model from: {MODEL_PATH}")
    model = lgb.Booster(model_file=MODEL_PATH)
    logger.info("✅ Model loaded successfully")
except FileNotFoundError:
    logger.error(f"Model file not found at: {MODEL_PATH}")
    model = None
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """Root endpoint - checks if service is running."""
    return {"status": "ok", "service": "Amazon Review Predictor API"}

@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    return {"status": "healthy", "model_loaded": True}

# --- 2. Define Data Structures ---
class ReviewFeatures(BaseModel):
    user_avg: float
    user_count: int
    item_avg: float
    item_count: int
    popularity_tier: str
    rating_age: int
    summary_len: int
    helpfulness: float
    
    class Config:
        schema_extra = {
            "example": {
                "user_avg": 4.2,
                "user_count": 10,
                "item_avg": 4.5,
                "item_count": 50,
                "popularity_tier": "High",
                "rating_age": 30,
                "summary_len": 25,
                "helpfulness": 0.8
            }
        }

# --- 3. Preprocessing Helper ---
def preprocess_features(data: dict):
    """
    Handles all transformations (logs, mappings) before inference.
    
    Args:
        data: Dictionary with raw features
        
    Returns:
        List of preprocessed features for model inference
    """
    pop_mapping = {"Low": 0, "Medium": 1, "High": 2, "Very High": 3}
    
    # Safe log transformations
    user_count = data.get("user_count", 0)
    item_count = data.get("item_count", 0)
    log_user_count = np.log(user_count) if user_count > 0 else 0
    log_item_count = np.log(item_count) if item_count > 0 else 0
    
    # Safely get popularity tier, defaulting to 'Medium' if missing
    tier = data.get("popularity_tier", "Medium")
    tier_val = pop_mapping.get(tier, 1)

    # ⚠️ NOTE: The 1.0, 1.0 placeholder features below may need investigation
    # These seem to be fixed features - are they intentional or bugs?
    # Consider replacing with actual computed features if needed
    
    return [
        data.get("user_avg", 3.0),      # User's average rating
        1.0,                             # Placeholder - investigate!
        log_user_count,                  # Log of user's review count
        data.get("item_avg", 3.0),      # Item's average rating
        1.0,                             # Placeholder - investigate!
        log_item_count,                  # Log of item's review count
        tier_val,                        # Popularity tier (0-3)
        data.get("rating_age", 30),     # How old the review is
        data.get("summary_len", 20),    # Length of review summary
        data.get("helpfulness", 0.5)    # Helpfulness ratio
    ]

# --- 4. Endpoints ---
@app.post("/predict", tags=["Predictions"])
def predict_single(features: ReviewFeatures):
    """
    Predicts sentiment for a single review.
    
    Returns:
        - probability: Float between 0 and 1 (confidence for "Liked")
        - prediction: "Liked" if probability >= 0.5, else "Disliked"
    """
    if model is None:
        logger.error("Model not loaded - cannot make prediction")
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    
    try:
        # Convert Pydantic model to dictionary and preprocess
        feature_dict = features.dict()
        processed_array = np.array([preprocess_features(feature_dict)])
        
        # Inference
        prediction_prob = model.predict(processed_array)[0]
        
        logger.info(f"Prediction made: {prediction_prob:.4f}")
        
        return {
            "probability": float(prediction_prob),
            "prediction": "Liked" if prediction_prob >= 0.5 else "Disliked"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/batch-predict", tags=["Predictions"])
async def predict_batch(file: UploadFile = File(...)):
    """
    Predicts sentiment for a batch of reviews via CSV upload.
    
    Expected CSV columns:
    - user_avg, user_count, item_avg, item_count, popularity_tier, 
      rating_age, summary_len, helpfulness
    
    Returns:
        - batch_results: Array of predictions with original data
    """
    if model is None:
        logger.error("Model not loaded - cannot make batch prediction")
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    try:
        # Read the uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        logger.info(f"Processing batch with {len(df)} rows")
        
        # Preprocess every row in the dataframe
        processed_data = []
        for _, row in df.iterrows():
            processed_data.append(preprocess_features(row.to_dict()))
            
        # Batch inference
        predictions = model.predict(np.array(processed_data))
        
        # Append results to the dataframe and return as JSON records
        df['Prediction_Probability'] = predictions
        df['Prediction'] = ["Liked" if p >= 0.5 else "Disliked" for p in predictions]
        
        logger.info(f"Batch processing complete. {sum(predictions >= 0.5)} liked, {sum(predictions < 0.5)} disliked")
        
        return {"batch_results": df.to_dict(orient="records")}
    
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")
