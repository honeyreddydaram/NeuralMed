#!/usr/bin/env python3
"""
Master training script for OpenHealth CSV-based models.

Trains and saves artifacts for:
  - Heart Disease        → Artifacts/Heart_Disease/Heart_{Preprocessor,Model}.pkl
  - Breast Cancer        → Artifacts/Breast_Cancer_Disease/BCancer_{Preprocessor,Model}.pkl
  - Diabetes             → Artifacts/Diabetes_Disease/Diabetes_{Preprocessor,Model}.pkl
  - Parkinson's Disease  → Artifacts/Parkinsons_Disease/Parkinsons_Model.pkl
  - Liver Disease        → Artifacts/Liver_Disease/Liver_Model.pkl

Image-based models (Brain, Kidney, Lung, Malaria) require TensorFlow and large
image datasets; they cannot be trained here and are skipped.
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_breast_cancer, fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent


# ── helpers ───────────────────────────────────────────────────────────────────

def save_pkl(rel_path: str, obj) -> None:
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        pickle.dump(obj, f)
    print(f"    saved → {rel_path}")


def pick_best(models: dict, X_train, y_train, X_test, y_test):
    scores = {}
    for name, m in models.items():
        m.fit(X_train, y_train)
        scores[name] = accuracy_score(y_test, m.predict(X_test))
        print(f"    {name}: {scores[name]:.4f}")
    best_name = max(scores, key=scores.get)
    print(f"  → Best: {best_name}  (acc={scores[best_name]:.4f})")
    return models[best_name]


def section(title: str) -> None:
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


def to_binary(y: pd.Series, positive) -> pd.Series:
    """Map a categorical/string/numeric series to 0/1 given the positive class value."""
    # Flatten Categorical to plain strings/objects first
    if hasattr(y, "cat"):
        y = y.astype(str)
    return (y.astype(str) == str(positive)).astype(int)


# ── 1. Heart Disease ──────────────────────────────────────────────────────────
# OpenML 53 columns: age, sex, chest, resting_blood_pressure, serum_cholestoral,
#   fasting_blood_sugar, resting_electrocardiographic_results,
#   maximum_heart_rate_achieved, exercise_induced_angina, oldpeak, slope,
#   number_of_major_vessels, thal, class

def train_heart():
    section("Heart Disease")
    print("  Fetching dataset from OpenML …")
    h = fetch_openml(data_id=53, as_frame=True, parser="auto")
    df = h.frame.copy()

    rename = {
        "chest": "cp",
        "resting_blood_pressure": "trestbps",
        "serum_cholestoral": "chol",
        "fasting_blood_sugar": "fbs",
        "resting_electrocardiographic_results": "restecg",
        "maximum_heart_rate_achieved": "thalach",
        "exercise_induced_angina": "exang",
        "number_of_major_vessels": "ca",
        "class": "target",
    }
    df = df.rename(columns=rename)

    feature_cols = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    df = df.dropna(subset=feature_cols + ["target"])
    X = df[feature_cols].astype(float)
    y = to_binary(df["target"], "present")  # 'present'=disease, 'absent'=healthy

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": GaussianNB(),
        "Random Forest": RandomForestClassifier(random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "KNN": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "SVM": SVC(probability=True, random_state=42),
    }
    best = pick_best(models, Xtr, y_train, Xte, y_test)
    best.fit(Xtr, y_train)

    save_pkl("Artifacts/Heart_Disease/Heart_Preprocessor.pkl", scaler)
    save_pkl("Artifacts/Heart_Disease/Heart_Model.pkl", best)


# ── 2. Breast Cancer ─────────────────────────────────────────────────────────
# sklearn built-in; 22 features match what BCancer prediction pipeline sends.

def train_breast_cancer():
    section("Breast Cancer")
    print("  Using sklearn built-in dataset …")
    bc = load_breast_cancer(as_frame=True)
    df = bc.frame.copy()

    selected = [
        "mean texture", "mean smoothness", "mean compactness", "mean concave points",
        "mean symmetry", "mean fractal dimension",
        "texture error", "area error", "smoothness error", "compactness error",
        "concavity error", "concave points error", "symmetry error", "fractal dimension error",
        "worst texture", "worst area", "worst smoothness", "worst compactness",
        "worst concavity", "worst concave points", "worst symmetry", "worst fractal dimension",
    ]
    X = df[selected]
    y = df["target"]  # 0=malignant, 1=benign

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Naive Bayes": GaussianNB(),
        "Random Forest": RandomForestClassifier(random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=10),
        "Decision Tree": DecisionTreeClassifier(criterion="entropy", max_depth=6, random_state=42),
        "SVM": SVC(kernel="rbf", gamma=0.1, C=1.0, probability=True, random_state=42),
    }
    best = pick_best(models, X_train, y_train, X_test, y_test)
    best.fit(X_train, y_train)

    # Prediction pipeline loads a preprocessor but never calls transform — save a passthrough
    passthrough = StandardScaler()
    passthrough.fit(X_train)

    save_pkl("Artifacts/Breast_Cancer_Disease/BCancer_Preprocessor.pkl", passthrough)
    save_pkl("Artifacts/Breast_Cancer_Disease/BCancer_Model.pkl", best)


# ── 3. Diabetes ───────────────────────────────────────────────────────────────
# OpenML 37 columns: preg, plas, pres, skin, insu, mass, pedi, age, class
# Prediction pipeline sends them scaled via Diabetes_Preprocessor.pkl.

def train_diabetes():
    section("Diabetes")
    print("  Fetching Pima Indians dataset from OpenML …")
    d = fetch_openml(data_id=37, as_frame=True, parser="auto")
    df = d.frame.copy()

    rename = {
        "preg": "Pregnancies", "plas": "Glucose", "pres": "BloodPressure",
        "skin": "SkinThickness", "insu": "Insulin", "mass": "BMI",
        "pedi": "DiabetesPedigreeFunction", "age": "Age", "class": "Outcome",
    }
    df = df.rename(columns=rename)

    feature_cols = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
    df = df.dropna(subset=feature_cols + ["Outcome"])
    X = df[feature_cols].astype(float)
    y = to_binary(df["Outcome"], "tested_positive")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": GaussianNB(),
        "Random Forest": RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=10),
        "Decision Tree": DecisionTreeClassifier(criterion="entropy", max_depth=6, random_state=42),
        "SVM": SVC(kernel="rbf", C=2, probability=True, random_state=42),
    }
    best = pick_best(models, Xtr, y_train, Xte, y_test)
    best.fit(Xtr, y_train)

    save_pkl("Artifacts/Diabetes_Disease/Diabetes_Preprocessor.pkl", scaler)
    save_pkl("Artifacts/Diabetes_Disease/Diabetes_Model.pkl", best)


# ── 4. Parkinson's Disease ────────────────────────────────────────────────────
# OpenML 'parkinsons' columns: V1-V22, Class
# UCI column order (name removed): MDVP:Fo(Hz)=V1, Fhi=V2, Flo=V3,
#   Jitter(%)=V4, …, RPDE=V17, DFA=V18, spread1=V19, spread2=V20, D2=V21, PPE=V22

def train_parkinsons():
    section("Parkinson's Disease")
    print("  Fetching UCI Parkinson's dataset from OpenML …")
    p = fetch_openml("parkinsons", as_frame=True, parser="auto")
    df = p.frame.copy()

    # Map positional Vn columns to UCI feature names
    uci_order = [
        "MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)", "MDVP:Jitter(%)",
        "MDVP:Jitter(Abs)", "MDVP:RAP", "MDVP:PPQ", "Jitter:DDP",
        "MDVP:Shimmer", "MDVP:Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5",
        "MDVP:APQ", "Shimmer:DDA", "NHR", "HNR",
        "RPDE", "DFA", "spread1", "spread2", "D2", "PPE",
    ]
    rename = {f"V{i+1}": name for i, name in enumerate(uci_order)}
    rename["Class"] = "status"
    df = df.rename(columns=rename)

    feature_cols = ["MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)", "MDVP:Jitter(%)",
                    "RPDE", "DFA", "spread2", "D2"]
    df = df.dropna(subset=feature_cols + ["status"])
    X = df[feature_cols].astype(float)
    y = to_binary(df["status"], "1")  # '1'=Parkinson's patient, '2'=healthy

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": GaussianNB(),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "Decision Tree": DecisionTreeClassifier(criterion="entropy", max_depth=6, random_state=42),
        "KNN": KNeighborsClassifier(),
        "Extra Trees": ExtraTreesClassifier(random_state=42),
    }
    best = pick_best(models, X_train, y_train, X_test, y_test)
    best.fit(X_train, y_train)

    # Prediction pipeline path: Artifacts/Parkinsons_Disease/Parkinsons_Model.pkl
    save_pkl("Artifacts/Parkinsons_Disease/Parkinsons_Model.pkl", best)


# ── 5. Liver Disease ─────────────────────────────────────────────────────────
# OpenML 1480 columns: V1-V10, Class
# Order: Age, Gender, Total_Bilirubin, Direct_Bilirubin, Alkaline_Phosphotase,
#   Alamine_Aminotransferase, Aspartate_Aminotransferase, Total_Proteins,
#   Albumin, Albumin_Globulin_Ratio, Class(1=patient,2=not)

def train_liver():
    section("Liver Disease")
    print("  Fetching Indian Liver Patient Dataset from OpenML …")
    l = fetch_openml(data_id=1480, as_frame=True, parser="auto")
    df = l.frame.copy()

    ilpd_cols = ["age", "gender", "total_bilirubin", "direct_bilirubin",
                 "alkaline_phosphotase", "alamine_aminotransferase",
                 "aspartate_aminotransferase", "total_proteins",
                 "albumin", "albumin_globulin_ratio"]
    rename = {f"V{i+1}": name for i, name in enumerate(ilpd_cols)}
    rename["Class"] = "target"
    df = df.rename(columns=rename)

    # Encode gender: Male→1, Female→0  (matches what liver.html form sends)
    df["gender"] = df["gender"].astype(str).str.strip().str.lower().map(
        {"male": 1, "m": 1, "female": 0, "f": 0}
    ).fillna(0).astype(int)

    feature_cols = ilpd_cols
    df = df.dropna(subset=feature_cols + ["target"])
    X = df[feature_cols].astype(float)
    y = to_binary(df["target"], "1")  # '1'=liver patient, '2'=healthy

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # app.py calls predict_proba → all models here support it
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    }
    best = pick_best(models, X_train, y_train, X_test, y_test)
    best.fit(X_train, y_train)

    save_pkl("Artifacts/Liver_Disease/Liver_Model.pkl", best)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.chdir(ROOT)

    trainers = [
        ("Heart Disease",    train_heart),
        ("Breast Cancer",    train_breast_cancer),
        ("Diabetes",         train_diabetes),
        ("Parkinson's",      train_parkinsons),
        ("Liver Disease",    train_liver),
    ]

    failed = []
    for name, fn in trainers:
        try:
            fn()
        except Exception as e:
            import traceback
            print(f"\n  ERROR in {name}: {e}")
            traceback.print_exc()
            failed.append(name)

    print(f"\n{'='*60}")
    succeeded = [n for n, _ in trainers if n not in failed]
    print(f"  Succeeded ({len(succeeded)}/5): {', '.join(succeeded) or 'none'}")
    if failed:
        print(f"  Failed    ({len(failed)}/5): {', '.join(failed)}")
    print("="*60)
    print("\nNote: Brain, Kidney, Lung, and Malaria image models require")
    print("TensorFlow (Python 3.10–3.12) and large image datasets (dvc pull).")
