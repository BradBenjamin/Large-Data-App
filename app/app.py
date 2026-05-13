import streamlit as st
import lightgbm as lgb
import numpy as np
import time
import os # Make sure to import os!

# --- Page Configuration ---
st.set_page_config(page_title="Review Predictor", page_icon="🛒", layout="centered")

# --- 1. Load the Model ---
@st.cache_resource
def load_model():
    """Loads the LightGBM model efficiently using dynamic absolute paths."""
    try:
        # 1. Get the directory where this app.py file lives (the /app folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Build the path: go up one level (".."), then into "model", then the file
        model_path = os.path.join(current_dir, "..", "model", "amazon_lgb_model.txt")
        
        # 3. Resolve it to a clean absolute path (e.g., C:/User/Project/model/amazon_lgb_model.txt)
        model_path = os.path.abspath(model_path)
        
        # 4. Load the model
        return lgb.Booster(model_file=model_path)
    
    except Exception as e:
        # If it fails, print the attempted path so you can debug easily
        st.error(f"Error loading model. Attempted path: {model_path}\nError details: {e}")
        return None

model = load_model()

# --- 2. Build the UI ---
st.title("🛒 Amazon Fine Food: Review Predictor")
st.markdown("Predict whether a user will **Like** (≥ 4 stars) or **Dislike** (< 4 stars) a product. Adjust the features below.")

# Create a clean layout with two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("User & Item Stats")
    # Streamlit automatically handles base validation (min/max values)
    user_avg = st.slider("User's Historical Avg Rating", 1.0, 5.0, 4.2, help="Average rating given by this user in the past.")
    user_count = st.number_input("User's Total Reviews (Count)", min_value=1, value=10, help="Total number of reviews written by this user.")
    item_avg = st.slider("Item's Global Avg Rating", 1.0, 5.0, 4.5, help="Average rating this product has received overall.")
    item_count = st.number_input("Item's Total Reviews (Count)", min_value=1, value=50, help="Total number of reviews this product has.")

with col2:
    st.subheader("Contextual Features")
    popularity_tier = st.selectbox("Item Popularity Tier", options=["Low", "Medium", "High", "Very High"])
    rating_age = st.number_input("Rating Age (Days ago)", min_value=0, value=30)
    summary_len = st.number_input("Review Summary Length (Chars)", min_value=0, value=25)
    helpfulness = st.slider("Helpfulness Ratio (Upvotes / Total Votes)", 0.0, 1.0, 0.8)

# --- 3. Process Inputs for the Model ---
pop_mapping = {"Low": 0, "Medium": 1, "High": 2, "Very High": 3}
log_user_count = np.log(user_count) if user_count > 0 else 0
log_item_count = np.log(item_count) if item_count > 0 else 0

features = np.array([[
    user_avg, 1.0, log_user_count, 
    item_avg, 1.0, log_item_count, 
    pop_mapping[popularity_tier], rating_age, summary_len, helpfulness
]])

# --- 4. Model Inference & Output ---
st.divider()

if st.button("🔮 Predict User Reaction", use_container_width=True):
    if model is None:
        st.error("Model failed to load. Please check the model file.")
    else:
        # Improved UX: Loading indicator 
        with st.spinner("Analyzing parameters..."):
            time.sleep(0.5) # Simulated brief delay for UX feel
            try:
                # Fast and reproducible inference 
                prediction_prob = model.predict(features)[0]
                
                # Clear outputs 
                if prediction_prob >= 0.5:
                    st.success(f"### 🎉 Prediction: LIKED! \n**Confidence:** {prediction_prob * 100:.2f}%")
                else:
                    st.error(f"### 👎 Prediction: DISLIKED. \n**Confidence:** {(1 - prediction_prob) * 100:.2f}%")
            except Exception as e:
                # Proper validation/error handling 
                st.error(f"An error occurred during prediction: {e}")