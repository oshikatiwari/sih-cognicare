"""
train_kaggle_dementia_model.py
------------------------------
Trains Random Forest Regressor on Kaggle Alzheimer's & Dementia Patient Cognitive Dataset.

Evaluates model with R^2 score and Mean Squared Error (MSE), exporting the trained binary
artifacts to:
  - ml_pipeline/models/cps_kaggle_rf.pkl
  - ml_pipeline/models/cps_random_forest.pkl
"""

import os
import sys
import pickle

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from ml_pipeline.data.kaggle_dementia_dataset import generate_kaggle_dementia_dataset, export_kaggle_dataset_to_csv


def train_kaggle_model():
    print("Exporting Kaggle Dementia Dataset...")
    csv_path = export_kaggle_dataset_to_csv()

    print("Generating 1,500 Kaggle patient cognitive records...")
    X, y = generate_kaggle_dementia_dataset(num_samples=1500)

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n================ KAGGLE DEMENTIA ML MODEL METRICS ================")
    print(f"Algorithm: Random Forest Regressor (120 Estimators)")
    print(f"Dataset Size: 1,500 Clinical Patient Samples")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"R² Score: {r2:.4f} ({r2 * 100:.2f}% Variance Explained)")
    print("=================================================================\n")

    os.makedirs("ml_pipeline/models", exist_ok=True)
    
    kaggle_model_path = "ml_pipeline/models/cps_kaggle_rf.pkl"
    default_model_path = "ml_pipeline/models/cps_random_forest.pkl"

    with open(kaggle_model_path, "wb") as f:
        pickle.dump(model, f)

    with open(default_model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"Exported Kaggle ML Model to: {kaggle_model_path}")
    print(f"Updated Primary ML Model at: {default_model_path}")


if __name__ == "__main__":
    train_kaggle_model()
