# 🛒 Amazon Fine Food: Review Predictor (Phase 6)

This repository contains the production deployment of the Phase 5 machine learning pipeline. It transitions the exploratory machine learning models into an interactive, real-world application featuring a microservice architecture (FastAPI backend + Streamlit frontend).

## 🚀 Execution Instructions

This application is packaged as a runnable desktop deployment following the required phase guidelines.

**Prerequisites:** Ensure you have Python 3.8+ installed.

### Option A: Easy Start (Windows Only)
If you are on a Windows machine, a batch script is provided to automate the setup:
1. Open this folder in File Explorer.
2. Double-click the `start.bat` file.
3. The script will automatically activate the virtual environment, boot both servers, and open the app in your browser!

### Option B: Manual Start (Mac / Linux / Windows)
If you are on a Mac, Linux, or prefer using the terminal:
1. Open your terminal and navigate to this project folder.
2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install the required dependencies:
   pip install -r requirements.txt
4. Run the master launch script:
   python run_app.py
5. The application will automatically open in your default web browser at http://localhost:8501.

---

## ⚙️ Performance & Scalability Considerations

* **Latency (Response Time):** LightGBM is inherently optimized for fast inference. Generating a prediction on a single instance of 10 features takes less than a millisecond. The UI response is practically instantaneous. Batch predictions via the FastAPI endpoint process hundreds of rows in under a second.
* **Memory Usage:** The memory footprint is low. The trained LightGBM model (`amazon_lgb_model.txt`) is highly compressed. The FastAPI and Streamlit servers require roughly 100-150MB of RAM combined to maintain the session state and UI components, which easily runs on standard hardware.
* **Scalability Limits:** Since the current architecture runs locally, it can handle tens of concurrent users. However, because we have decoupled the model inference into a dedicated API endpoint (FastAPI), this architecture is primed for cloud scalability. For massive scale, the FastAPI backend could be containerized via Docker and placed behind a load balancer.

---

## 🌍 Impact Evaluation & Implications

As part of transitioning to a real-world solution, the following implications must be considered:

### 1. Business Impact
Deploying this model allows e-commerce platforms or individual sellers to dynamically predict how a user will react to a product. Sellers can use this logic to proactively recommend items with high "Like" probabilities, thereby increasing customer satisfaction, boosting conversion rates, and reducing return rates.

### 2. Risks and Limitations
* **Concept Drift:** Consumer tastes change over time. A model trained on past reviews may slowly degrade in accuracy as new trends emerge.
* **The "Cold Start" Problem:** The model relies heavily on historical averages (`User's Historical Avg Rating`, `Item's Global Avg Rating`). For brand-new users or newly launched products with zero reviews, the model's predictions will be less reliable because the logging transformations fall back to default minimums.

### 3. Ethical and Societal Implications
* **Algorithmic Bias against New Sellers:** Because the model considers the "Item's Total Reviews" and "Popularity Tier," there is a risk of creating a feedback loop where already popular items are predicted to be liked, while new, high-quality products from emerging sellers are systematically disadvantaged. 
* **Echo Chambers:** If this predictor is tied directly to a recommendation engine, users may only be shown items the model *knows* they will like, isolating them from discovering diverse or novel products.
