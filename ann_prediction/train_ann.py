
from pathlib import Path
import numpy as np
import tensorflow as tf
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from ann_prediction.preprocessing import prepare_data, MODEL_DIR


# Load preprocessed data
X, y, classes = prepare_data()

# Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Build ANN model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1],)),

    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dropout(0.3),

    tf.keras.layers.Dense(8, activation="relu"),

    tf.keras.layers.Dense(len(classes), activation="softmax")
])

# Compile model
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Early stopping
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

# Train ANN
history = model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=4,
    validation_split=0.2,
    callbacks=[early_stopping],
    verbose=1
)

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

print("\nANN Evaluation")
print("--------------------")
print("Test Accuracy:", round(accuracy * 100, 2), "%")

# Generate predictions
y_pred_prob = model.predict(X_test, verbose=0)
y_pred = np.argmax(y_pred_prob, axis=1)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=np.arange(len(classes)),
        target_names=classes,
        zero_division=0
    )
)

# Save trained ANN model
model.save(MODEL_DIR / "inventory_demand_ann.keras")

print("\nANN model saved successfully!")
