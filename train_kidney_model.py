#!/usr/bin/env python3
"""
Train the Kidney Disease Detection model and save to Artifacts/Kidney_Disease/Kidney_Model.h5

Dataset layout expected:
    <data_dir>/{Cyst,Normal,Stone,Tumor}/   (all images in one directory, no pre-split)

Usage:
    python train_kidney_model.py --data "datasets/ct-kidney-dataset /CT-KIDNEY-DATASET-Normal-Cyst-Tumor-Stone/CT-KIDNEY-DATASET-Normal-Cyst-Tumor-Stone"
"""

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout, BatchNormalization

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "Artifacts" / "Kidney_Disease" / "Kidney_Model.h5"
IMG_SIZE = (150, 150)
BATCH_SIZE = 32
EPOCHS = 15


def main(data_dir: str):
    data_dir = Path(data_dir).expanduser().resolve()

    classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
    print(f"Classes found: {classes}")
    if set(classes) != {"Cyst", "Normal", "Stone", "Tumor"}:
        raise ValueError(f"Expected Cyst/Normal/Stone/Tumor folders, got: {classes}")

    print("Loading dataset …")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        str(data_dir),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="training",
        seed=42,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        str(data_dir),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="validation",
        seed=42,
    )

    # Normalize to [0, 1]
    normalization = tf.keras.layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (normalization(x), y)).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (normalization(x), y)).prefetch(tf.data.AUTOTUNE)

    print("Building VGG16 model …")
    base = tf.keras.applications.VGG16(
        include_top=False, weights="imagenet",
        input_shape=(150, 150, 3), pooling="max",
    )
    base.trainable = False

    model = Sequential([
        base,
        Flatten(),
        Dense(512, activation="relu"),
        BatchNormalization(),
        Dropout(0.5),
        Dense(4, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.summary()

    print(f"\nTraining for {EPOCHS} epochs …")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    print("\nEvaluating …")
    loss, acc = model.evaluate(val_ds, verbose=1)
    print(f"Validation accuracy: {acc * 100:.2f}%")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(OUT_PATH))
    print(f"\nModel saved → {OUT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train kidney disease detection model")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to CT-KIDNEY-DATASET-Normal-Cyst-Tumor-Stone folder (contains Cyst/Normal/Stone/Tumor)",
    )
    args = parser.parse_args()
    main(args.data)
