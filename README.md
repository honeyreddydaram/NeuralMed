# NeuralMed — Deep Learning for Deeper Health Insights

A multi-disease clinical screening platform combining classical ML, deep learning, and LLM-augmented health guidance.  
**Deliverable 3 — Refined Prototype**

---

## System Overview

NeuralMed is a Flask-based web application providing disease screening across six modalities through two portals:

- **Patient Portal** — educational predictions with plain-language AI explanations
- **Doctor Portal** *(new in D3)* — clinical decision support with confidence %, feature importance, reference ranges, and Gemini-powered clinical summaries

| Module | Model | D3 Test Acc | 5-Fold CV | AUC |
|---|---|---|---|---|
| Diabetes | GaussianNB | 74.7% | 76.0 ± 1.7% | 0.84 |
| Heart Disease | Naive Bayes | 85.2% | 84.1 ± 4.3% | 0.92 |
| Parkinson's | Random Forest (depth=10) | 92.3% | 88.2 ± 4.8% | 0.97 |
| Liver Disease | Logistic Regression | 69.2% | 71.9 ± 3.4% | 0.77 |
| Breast Cancer | Logistic Regression | 98.2% | 97.4 ± 1.7% | 0.99 |
| Kidney CT | VGG-16 Transfer Learning | 99.0% | — | — |

---

## Key Improvements: D2 → D3

| Area | D2 | D3 |
|---|---|---|
| Overfitting | RF/DT at 100% (suspected overfit) | max_depth=10 constraint + 5-fold CV |
| Evaluation | Single train/test split | 5-fold stratified CV + confusion matrices + ROC |
| UI | Materialize carousel | Complete dark design system (main.css) |
| Doctor Tools | None | Confidence %, feature importance, reference ranges, PDF export |
| AI Chatbot | Separate Streamlit app | Embedded on landing page with retry logic |
| Gemini API | Deprecated `gemini-pro` | Updated to `gemini-2.5-flash-lite` |
| Error handling | Broad `except` swallowing errors | Typed handlers + graceful fallback messages |

---

## Setup and Running

```bash
git clone https://github.com/honeyreddydaram/Deep-Learning-Project.git
cd Deep-Learning-Project
conda create -n neuralmed python=3.11 -y
conda activate neuralmed
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key_here" > .env
dvc pull          # download model artifacts
python app.py     # opens at http://localhost:5001
```

---

## Running the D3 Evaluation Notebook

```bash
cd Notebook_Experiments
jupyter notebook D3_Evaluation_Refinements.ipynb
```

Reproduces: 5-fold CV, confusion matrices, ROC curves, feature importance, D2 vs D3 comparison.

---

## Project Structure

```
Deep-Learning-Project/
├── app.py                              # Flask app — patient + doctor portal routes
├── train_all.py                        # Tabular model training script
├── train_kidney_model.py               # VGG-16 kidney CNN trainer
├── requirements.txt
├── data/                               # Raw datasets (CSV)
├── Artifacts/                          # Trained .pkl and .h5 files (DVC tracked)
├── Notebook_Experiments/
│   ├── D3_Evaluation_Refinements.ipynb # D3 extended evaluation notebook (NEW)
│   └── ... (9 per-disease notebooks)
├── src/
│   ├── utils.py                        # Gemini client, model utilities
│   └── Multi_Disease_System/           # Per-disease pipeline components
├── static/css/main.css                 # NeuralMed design system
├── templates/                          # 21 HTML templates (patient + doctor portal)
├── results/                            # Evaluation plots + metrics_summary.json
└── docs/                               # Screenshots and architecture diagrams
```

---

## Updated Performance Results

See `results/metrics_summary.json` for full per-model metrics.  
Key plots in `results/`:
- `cv_all_models.png` — 5-fold CV across all 8 models × 5 diseases
- `confusion_matrices.png` — best model per disease
- `roc_curves.png` — ROC + AUC per disease
- `d2_vs_d3_comparison.png` — D2 vs D3 accuracy side-by-side
- `feature_importance.png` — top-10 feature importances
- `cv_boxplots.png` — model stability analysis

---

## Known Issues

- **Brain tumor + lung** routes show placeholder messages (no trained artifacts deployed)
- **Kidney** requires TensorFlow (Python 3.10–3.12); inference uses subprocess isolation
- **Gemini API key** required for chatbot, doctor summaries, and educational LLM routes
- **Not for clinical use** — all outputs are decision-support aids only, not diagnoses

---

## Contact

**Honey Reddy Daram**  
Department of Artificial Intelligence Systems, University of Florida  
honeyreddydaram@ufl.edu
