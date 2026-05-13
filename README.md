# 🛒 Amazon Fine Food: Review Predictor (Phase 6)

This repository contains the production deployment of the Phase 5 machine learning pipeline. [cite_start]It transitions the exploratory machine learning models into an interactive, real-world application[cite: 52].

## 🚀 Execution Instructions

[cite_start]This application is packaged as a runnable desktop deployment. 

**Prerequisites:** Ensure you have Python 3.8+ installed.

1. **Open your terminal or command prompt** and navigate to this folder.

2. **(Optional but recommended)** Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. **Install the required dependencies:**
pip install -r requirements.txt

4. **Run the application:**
streamlit run app.py

5. **The application will automatically open in your default web browser at**
http://localhost:8501


# ⚙️ Performance & Scalability Considerations

Latency (Response Time): LightGBM is inherently optimized for fast inference. Generating a prediction on a single instance of 10 features takes less than a millisecond. The UI response is practically instantaneous, creating a seamless user experience.  

Memory Usage: The memory footprint is very low. The trained LightGBM model (amazon_lgb_model.txt) is highly compressed. The Streamlit server requires roughly 50-100MB of RAM to maintain the session state and UI components, which easily runs on standard hardware.

Scalability Limits: Since the current architecture runs on a synchronous local Streamlit server, it can handle tens of concurrent users easily. However, if deployed to a high-traffic environment, Streamlit might suffer from thread blocking. For massive scale, the model inference would need to be decoupled into a dedicated API endpoint (e.g., using FastAPI) and placed behind a load balancer.


# 🌍 Impact Evaluation & Implications
As part of transitioning to a real-world solution, the following implications must be considered:  

1. Business Impact
Deploying this model allows e-commerce platforms or individual sellers to dynamically predict how a user will react to a product. Sellers can use this logic to proactively recommend items with high "Like" probabilities, thereby increasing customer satisfaction, boosting conversion rates, and reducing return rates.

2. Risks and Limitations
Concept Drift: Consumer tastes change over time. A model trained on past reviews may slowly degrade in accuracy as new trends emerge.

The "Cold Start" Problem: The model relies heavily on historical averages (User's Historical Avg Rating, Item's Global Avg Rating). For brand-new users or newly launched products with zero reviews, the model's predictions will be less reliable because the logging transformations fall back to default minimums.

3. Ethical and Societal Implications
Algorithmic Bias against New Sellers: Because the model considers the "Item's Total Reviews" and "Popularity Tier," there is a risk of creating a feedback loop where already popular items are predicted to be liked, while new, high-quality products from emerging sellers are systematically disadvantaged.

Echo Chambers: If this predictor is tied directly to a recommendation engine, users may only be shown items the model knows they will like, isolating them from discovering diverse or novel products.