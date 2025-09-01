import joblib

from models.random_forest_training import best_rf

joblib.dump(best_rf, '../models/rf_earthquake_model_tuned.pkl')

import joblib

# Load your trained Random Forest model
rf_model = joblib.load('../models/rf_earthquake_model_tuned.pkl')
print("✅ Model loaded successfully")