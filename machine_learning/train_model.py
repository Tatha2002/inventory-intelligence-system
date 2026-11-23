
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, ConfusionMatrixDisplay

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_inventory.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
VISUALIZATION_DIR = os.path.join(BASE_DIR, "visualizations")

TARGET = "historical_demand_label"
NUMERIC_FEATURES = ["stock_quantity", "reorder_level", "order_count", "return_count", "selling_price"]
CATEGORICAL_FEATURES = ["category", "brand", "warehouse", "supplier_code"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Cleaned dataset not found. Run ml_preprocessing.py first.")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET].astype(str)
    if y.nunique() < 2:
        raise ValueError("At least two target classes are required for model training.")
    return X, y

def create_preprocessor():
    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_pipeline = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("numeric", numeric_pipeline, NUMERIC_FEATURES), ("categorical", categorical_pipeline, CATEGORICAL_FEATURES)])

def train_models():
    X, y = load_data()
    class_counts = y.value_counts()
    stratify = y if class_counts.min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=stratify)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    }

    results = {}
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)

    for name, classifier in models.items():
        model = Pipeline([("preprocessor", create_preprocessor()), ("classifier", classifier)])
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, average="weighted", zero_division=0),
            "recall": recall_score(y_test, predictions, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, predictions, average="weighted", zero_division=0)
        }

        print(f"\n{name}")
        print("Accuracy:", results[name]["accuracy"])
        print("Precision:", results[name]["precision"])
        print("Recall:", results[name]["recall"])
        print("F1-score:", results[name]["f1_score"])
        print(classification_report(y_test, predictions, zero_division=0))

        labels = model.classes_
        matrix = confusion_matrix(y_test, predictions, labels=labels)
        display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels)
        display.plot(cmap="Blues")
        plt.title(f"{name} Confusion Matrix")
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, name.lower().replace(" ", "_") + "_confusion_matrix.png"))
        plt.close()

    best_name = max(results, key=lambda name: results[name]["f1_score"])
    best_model = results[best_name]["model"]

    with open(os.path.join(MODEL_DIR, "demand_model.pkl"), "wb") as file:
        pickle.dump(best_model, file)

    metadata = {"model_name": best_name, "features": FEATURES, "target": TARGET, "classes": list(best_model.classes_)}

    with open(os.path.join(MODEL_DIR, "model_metadata.pkl"), "wb") as file:
        pickle.dump(metadata, file)

    print("\nBest Model:", best_name)
    print("Model saved successfully.")
    return results

if __name__ == "__main__":
    train_models()
