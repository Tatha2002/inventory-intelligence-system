
import pandas as pd
import pickle
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


# Dataset path
BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR / "machine_learning" / "data" / "cleaned_inventory.csv"
)

MODEL_DIR = Path(__file__).resolve().parent / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# Input features
NUMERIC_FEATURES = [
    "stock_quantity",
    "reorder_level",
    "order_count",
    "return_count",
    "selling_price"
]

CATEGORICAL_FEATURES = [
    "category",
    "brand",
    "warehouse",
    "supplier_code"
]

TARGET = "historical_demand_label"


def prepare_data():

    # Load dataset
    df = pd.read_csv(DATASET_PATH)

    # Separate features and target
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET].astype(str)

    # Numerical preprocessing
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Categorical preprocessing
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Combine preprocessing
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES)
    ])

    # Transform input features
    X_processed = preprocessor.fit_transform(X)

    # Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Save preprocessing objects
    with open(MODEL_DIR / "preprocessor.pkl", "wb") as file:
        pickle.dump(preprocessor, file)

    with open(MODEL_DIR / "label_encoder.pkl", "wb") as file:
        pickle.dump(label_encoder, file)

    return X_processed, y_encoded, label_encoder.classes_


if __name__ == "__main__":

    X, y, classes = prepare_data()

    print("Preprocessing completed!")
    print("Input shape:", X.shape)
    print("Target shape:", y.shape)
    print("Classes:", classes)
