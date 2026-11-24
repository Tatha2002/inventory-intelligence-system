
import pickle
import numpy as np
import pandas as pd

from pathlib import Path
from tensorflow.keras.models import load_model

from ann_prediction.preprocessing import (
    MODEL_DIR,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES
)


# Load saved ANN model
MODEL_PATH = MODEL_DIR / "inventory_demand_ann.keras"

model = load_model(MODEL_PATH)

# Load preprocessing objects
with open(MODEL_DIR / "preprocessor.pkl", "rb") as file:
    preprocessor = pickle.load(file)

with open(MODEL_DIR / "label_encoder.pkl", "rb") as file:
    label_encoder = pickle.load(file)


def predict_demand(features):

    # Convert input dictionary into DataFrame
    input_data = pd.DataFrame(
        [features],
        columns=NUMERIC_FEATURES + CATEGORICAL_FEATURES
    )

    # Apply previously fitted preprocessing
    processed_data = preprocessor.transform(input_data)

    # Predict probabilities
    probabilities = model.predict(processed_data, verbose=0)[0]

    # Get predicted class
    predicted_index = np.argmax(probabilities)

    predicted_label = label_encoder.inverse_transform(
        [predicted_index]
    )[0]

    confidence = float(probabilities[predicted_index]) * 100

    return {
        "predicted_demand": predicted_label,
        "confidence": round(confidence, 2)
    }

if __name__ == "__main__":

    sample_product = {
        "stock_quantity": 50,
        "reorder_level": 20,
        "order_count": 100,
        "return_count": 5,
        "selling_price": 500,
        "category": "Electronics",
        "brand": "Samsung",
        "warehouse": "Kolkata",
        "supplier_code": "SUP001"
    }

    result = predict_demand(sample_product)

    print("Prediction:", result)