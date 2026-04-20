import warnings
warnings.simplefilter('ignore')

import os
import sys
import pickle
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")
os.chdir(ROOT_DIR)

from src.utils import text_model
from src.Multi_Disease_System.Parkinsons_Disease_Prediction.pipelines.Prediction_pipeline import Parkinsons_Data, PredictParkinsons
from src.Multi_Disease_System.Breast_Cancer_Prediction.pipelines.Prediction_pipeline import BCancer_Data, PredictBCancer
from src.Multi_Disease_System.Diabetes_Disease_Prediction.pipelines.Prediction_pipeline import Diabetes_Data, PredictDiabetes
from src.Multi_Disease_System.Heart_Disease_Prediction.pipelines.Prediction_pipeline import CustomData, PredictPipeline


def _artifact(*parts: str) -> Path:
    return ROOT_DIR / "Artifacts" / Path(*parts)


VALUES_DIR = ROOT_DIR / "values"
VALUES_DIR.mkdir(exist_ok=True)


def _save_inputs(module: str, fields: dict):
    """Append submitted form values to values/<module>.txt."""
    from datetime import datetime
    txt_path = VALUES_DIR / f"{module}.txt"
    with open(txt_path, "a") as f:
        f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for k, v in fields.items():
            f.write(f"{k}: {v}\n")
        f.write("\n")


def _save_image(module: str, file_storage):
    """Save an uploaded image to values/<module>.<ext>."""
    ext = Path(file_storage.filename).suffix or ".jpg"
    img_path = VALUES_DIR / f"{module}{ext}"
    file_storage.save(str(img_path))
    return img_path


_kidney_model = None
_liver_model = None


def get_kidney_model():
    global _kidney_model
    if _kidney_model is None:
        try:
            from tensorflow.keras.models import load_model as keras_load_model
        except ImportError as e:
            raise ImportError(
                "TensorFlow is required for kidney image prediction. "
                "Install with Python 3.10–3.12: pip install tensorflow"
            ) from e
        p = _artifact("Kidney_Disease", "Kidney_Model.h5")
        if not p.is_file():
            raise FileNotFoundError(
                f"Missing kidney model at {p}. From the project root run: dvc pull"
            )
        _kidney_model = keras_load_model(str(p))
    return _kidney_model


def get_liver_model():
    global _liver_model
    if _liver_model is None:
        p = _artifact("Liver_Disease", "Liver_Model.pkl")
        if not p.is_file():
            raise FileNotFoundError(
                f"Missing liver model at {p}. From the project root run: dvc pull"
            )
        with open(p, "rb") as f:
            _liver_model = pickle.load(f)
    return _liver_model



app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('landing.html')
    except:
        return render_template('error.html')
    
@app.route('/services')
def index1():
    try:
        return render_template('services.html')
    except:
        return render_template('error.html')
    
'''@app.route('/landing')
def other():
    return render_template('landing.html')'''

@app.route('/chatbot')
def run_streamlit():
    try:
        subprocess.Popen(["streamlit", "run", str(ROOT_DIR / "src" / "GeminiMed" / "app.py")])
        return redirect(url_for('index'))
    except:
        return render_template('error.html')


@app.route('/recognition')
def run_streamlit1():
    try:
        subprocess.Popen(["streamlit", "run", str(ROOT_DIR / "src" / "MedicineRecognition" / "app.py")])
        return redirect(url_for('index'))
    except:
        return render_template('error.html')

@app.route('/food/<disease>/<tumor_type>', methods=['GET', 'POST'])
def more_info(disease, tumor_type):
    if request.method == 'POST':
        prompt = f"Give me information about the {disease} for this suffering type {tumor_type} in the following paragraph format:\
        Disease Name: \
        Disease Description:\
        Disease Symptoms:\
        Disease Treatment:\
        Disease Food to Eat:\
        Disease Food to Avoid:"  
        # Generate information based on the disease and tumor type
        resp = text_model.generate_content(prompt)
        ans = (resp.text or "").replace("*", "\n") 
        return render_template("llm.html", answer=ans)
    return render_template("llm.html", disease=disease, tumor_type=tumor_type)


@app.route('/brain', methods=['GET', 'POST'])
def brain():
    return render_template(
        'brain_tumour.html',
        error='Brain Tumour Detection is currently unavailable.',
    )


@app.route('/bcancer', methods=["GET", "POST"])
def brain_post():
    if request.method == 'POST':
        try:
            _save_inputs('breast_cancer', dict(request.form))
            data = BCancer_Data(
                texture_mean = float(request.form['texture_mean']),
                smoothness_mean = float(request.form['smoothness_mean']),
                compactness_mean = float(request.form['compactness_mean']),
                concave_points_mean = float(request.form['concave_points_mean']),
                symmetry_mean = float(request.form['symmetry_mean']),
                fractal_dimension_mean = float(request.form['fractal_dimension_mean']),
                texture_se = float(request.form['texture_se']),
                area_se = float(request.form['area_se']),
                smoothness_se = float(request.form['smoothness_se']),
                compactness_se = float(request.form['compactness_se']),
                concavity_se = float(request.form['concavity_se']),
                concave_points_se = float(request.form['concave_points_se']),
                symmetry_se = float(request.form['symmetry_se']),
                fractal_dimension_se = float(request.form['fractal_dimension_se']),
                texture_worst = float(request.form['texture_worst']),
                area_worst = float(request.form['area_worst']),
                smoothness_worst = float(request.form['smoothness_worst']),
                compactness_worst = float(request.form['compactness_worst']),
                concavity_worst = float(request.form['concavity_worst']),
                concave_points_worst = float(request.form['concave_points_worst']),
                symmetry_worst = float(request.form['symmetry_worst']),
                fractal_dimension_worst = float(request.form['fractal_dimension_worst'])
                )
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictBCancer()
            pred = predict_pipeline.predict(final_data)
            result = 0 if int(pred[0]) == 1 else 1
            return render_template('bcancer.html', final_result=result)
        except Exception as e:
            return render_template('bcancer.html', error=str(e))
    return render_template('bcancer.html')

@app.route('/diabetes', methods=["GET", "POST"])
def diabetes():
    if request.method == "POST":
        try:
            _save_inputs('diabetes', dict(request.form))
            data = Diabetes_Data(
                pregnancies=request.form.get("pregnancies"),
                Glucose=request.form.get("Glucose"),
                BloodPressure=request.form.get("BloodPressure"),
                skin_thickness=request.form.get("skin_thickness"),
                insulin=request.form.get("insulin"),
                BMI=request.form.get("BMI"),
                DiabetesPedigreeFunction=request.form.get("DiabetesPedigreeFunction"),
                Age=request.form.get("Age"))
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictDiabetes()
            pred = predict_pipeline.predict(final_data)
            result = int(pred[0])
            return render_template("diabetes.html", final_result=result)
        except Exception as e:
            return render_template("diabetes.html", error=str(e))
    return render_template("diabetes.html")

@app.route('/heart', methods=["GET", "POST"])
def heart():
    if request.method == "POST":
        try:
            _save_inputs('heart', dict(request.form))
            data = CustomData(
                age=request.form.get("age"),
                sex=request.form.get("sex"),
                cp=(request.form.get("cp")),
                trestbps=(request.form.get("trestbps")),
                chol=(request.form.get("chol")),
                fbs=request.form.get("fbs"),
                restecg=request.form.get("restecg"),
                thalach=(request.form.get("thalach")),
                exang=request.form.get("exang"),
                oldpeak=request.form.get("oldpeak"),
                slope=request.form.get("slope"),
                ca=request.form.get("ca"),
                thal=(request.form.get("thal")))
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictPipeline()
            pred = predict_pipeline.predict(final_data)
            result = round(pred[0], 2)
            return render_template("heart.html", final_result=result)
        except:
            return render_template("error.html")
    return render_template("heart.html")

@app.route('/kidney', methods=['GET', 'POST'])
def kidney():
    if request.method == 'POST':
        try:
            class_labels = {0: 'Cyst', 1: 'Normal', 2: 'Stone', 3: 'Tumor'}
            file = request.files['file']
            if file.filename == '':
                return render_template('error.html', message='No file selected')
            _save_image('kidney', file)
            file.stream.seek(0)
            file_path = 'temp.jpg'
            file.save(file_path)
            model_path = str(_artifact("Kidney_Disease", "Kidney_Model.h5"))
            # Prefer the same interpreter that's running this server
            python = sys.executable
            result = subprocess.run(
                [python, str(ROOT_DIR / "kidney_predict.py"), file_path, model_path],
                capture_output=True, text=True, timeout=60, cwd=str(ROOT_DIR)
            )
            prediction_label = result.stdout.strip() or "Unknown"
            if os.path.exists(file_path):
                os.remove(file_path)
            return render_template('kidney.html', prediction=prediction_label)
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('kidney.html')

@app.route("/lung", methods=["GET", "POST"])
def lung():
    """Lung upload UI. No Keras lung model is shipped in Artifacts for this repo."""
    prediction = None
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename:
            prediction = "Please choose an image file before submitting."
        else:
            _save_image('lung', f)
            f.stream.seek(0)
            prediction = (
                "Lung X-ray classification is not enabled in this build (no model in Artifacts). "
                f"Uploaded: {f.filename}. "
                "Add a trained model and wire prediction in app.py to show class labels here."
            )
    return render_template("lung.html", prediction=prediction)


@app.route("/precautions")
def precautions():
    return render_template("precautions1.html")


@app.route('/liver', methods=['GET', 'POST'])
def liver():
    if request.method == 'POST':
        _save_inputs('liver', dict(request.form))
        age = float(request.form['age'])
        gender = int(request.form['gender'])
        total_bilirubin = float(request.form['total_bilirubin'])
        direct_bilirubin = float(request.form['direct_bilirubin'])
        alkaline_phosphotase = float(request.form['alkaline_phosphotase'])
        alamine_aminotransferase = float(request.form['alamine_aminotransferase'])
        aspartate_aminotransferase = float(request.form['aspartate_aminotransferase'])
        total_proteins = float(request.form['total_proteins'])
        albumin = float(request.form['albumin'])
        albumin_globulin_ratio = float(request.form['albumin_globulin_ratio'])
        
        # Preprocess features
        features = np.array([age, gender, total_bilirubin, direct_bilirubin, alkaline_phosphotase,
                            alamine_aminotransferase, aspartate_aminotransferase, total_proteins,
                            albumin, albumin_globulin_ratio]).reshape(1, -1)
        
        # Make prediction - (livermodel and liverpreprocessor assumed to be defined elsewhere)
        liver = get_liver_model()
        prediction = liver.predict(features)[0]
        probability = liver.predict_proba(features)[0][1]
        
        # Prepare response
        if prediction == 1:
            result = 'Positive'
        else:
            result = 'Negative'
        
        return render_template('liver.html', prediction=result)

    return render_template('liver.html')


@app.route('/malaria')
def malaria():
    try:
        return render_template('malaria.html')
    except:
        return render_template('error.html')
    

@app.route('/parkinsons', methods=["GET", "POST"])
def parkinsons():
    if request.method == 'POST':
        try:
            _save_inputs('parkinsons', dict(request.form))
            data = Parkinsons_Data(
                    MDVPFO=float(request.form.get("MDVPFO")),
                    MDVPFHI=float(request.form.get("MDVPFHI")),
                    MDVPFLO=float(request.form.get("MDVPFLO")),
                    MDVPJ=float(request.form.get("MDVPJ")),
                    RPDE=float(request.form.get("RPDE")),
                    DFA=float(request.form.get("DFA")),
                    spread2=float(request.form.get("spread2")),
                    D2=float(request.form.get("D2")))
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictParkinsons()
            pred = predict_pipeline.predict(final_data)
            result = int(pred[0])
            return render_template("parkinson.html", final_result=result)
        except Exception as e:
            return render_template("error.html")
    return render_template('parkinson.html')

def _education_prompt(topic: str) -> str:
    """General education only — not individualized medical advice."""
    intro = (
        "Respond in plain text with short sections and headings. "
        "This is general public health education, not a diagnosis. "
        "State that users must consult qualified clinicians for personal decisions.\n\n"
    )
    topics = {
        "general": "Give a brief overview of how AI-assisted health tools are used for education and why they cannot replace doctors.",
        "lung": "Explain what lung imaging (e.g. chest X-ray, CT) can and cannot show, common reasons for imaging, and red-flag symptoms that warrant urgent care. No diagnosis.",
        "kidney": "Explain kidney health basics: what kidney imaging and lab tests generally assess, and lifestyle tips often discussed for kidney wellness. No diagnosis.",
        "brain": "Explain brain imaging basics (e.g. MRI/CT) in simple terms and why follow-up with specialists matters for brain-related findings. No diagnosis.",
        "heart": "Explain heart disease risk factors (e.g. blood pressure, cholesterol, lifestyle) in educational terms and encourage professional cardiovascular care. No diagnosis.",
        "breast": "Explain breast cancer screening concepts in general educational terms (e.g. why screening exists, that results need clinical follow-up). No diagnosis.",
        "diabetes": "Explain diabetes types and why glucose control matters in general terms, and the role of clinicians and lifestyle. No diagnosis.",
        "parkinson": "Explain Parkinson's disease in general educational terms (symptoms families may notice, importance of neurology care). No diagnosis.",
        "malaria": "Explain malaria prevention and seeking care in general educational terms (mosquito bite prevention, symptoms that need medical attention). No diagnosis.",
    }
    body = topics.get(topic, topics["general"])
    return intro + body


@app.route("/llm")
def llm_standalone():
    """Educational LLM text; pass ?topic=lung|kidney|brain|heart|breast|diabetes|parkinson|malaria|general"""
    raw = (request.args.get("topic") or "general").strip().lower()
    allowed = {
        "general",
        "lung",
        "kidney",
        "brain",
        "heart",
        "breast",
        "bcancer",
        "diabetes",
        "parkinson",
        "parkinsons",
        "malaria",
    }
    topic = raw if raw in allowed else "general"
    if topic in ("bcancer", "parkinsons"):
        topic = "breast" if topic == "bcancer" else "parkinson"

    prompt = _education_prompt(topic)
    try:
        resp = text_model.generate_content(prompt)
        ans = (resp.text or "").replace("*", "\n")
    except Exception as e:
        err = str(e)
        if "quota" in err.lower() or "429" in err:
            ans = "AI explanations are temporarily unavailable — the API quota has been exceeded. Please try again later or visit a trusted health resource for general information."
        else:
            ans = "AI explanations are currently unavailable. Please consult a qualified healthcare professional for personalised advice."
    return render_template("llm.html", answer=ans)


@app.route('/brain_tumour1')
def brain_tumour1():
    prompt = f"Give me information about the brain disease for this suffering type glioma tumour in the following paragraph format:\
        Disease Name: \
        Disease Description:\
        Disease Symptoms:\
        Disease Treatment:\
        Disease Food to Eat:\
        Disease Food to Avoid:"  
        # Generate information based on the disease and tumor type
    resp = text_model.generate_content(prompt)
    ans = (resp.text or "").replace("*", "\n")
    return render_template("llm.html", answer=ans)

@app.route('/brain_tumour2')
def brain_tumour2():
    prompt = f"Give me information about the brain disease for this suffering type meningioma tumour in the following paragraph format:\
        Disease Name: \
        Disease Description:\
        Disease Symptoms:\
        Disease Treatment:\
        Disease Food to Eat:\
        Disease Food to Avoid:"  
        # Generate information based on the disease and tumor type
    resp = text_model.generate_content(prompt)
    ans = (resp.text or "").replace("*", "\n")
    return render_template("llm.html", answer=ans)

@app.route('/brain_tumour3')
def brain_tumour3():
    prompt = f"Give me information about the brain disease for this suffering type pituatary tumour in the following paragraph format:\
        Disease Name: \
        Disease Description:\
        Disease Symptoms:\
        Disease Treatment:\
        Disease Food to Eat:\
        Disease Food to Avoid:"  
        # Generate information based on the disease and tumor type
    resp = text_model.generate_content(prompt)
    ans = (resp.text or "").replace("*", "\n")
    return render_template("llm.html", answer=ans)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify({"reply": "Please type a message."})
    system_prompt = f"""You are NeuralMed AI, a friendly health assistant built into the NeuralMed web platform.

ABOUT THIS PLATFORM:
NeuralMed has the following tools users can access:
- Diabetes Prediction → /diabetes (8 clinical inputs)
- Heart Disease Prediction → /heart (13 inputs)
- Liver Disease Prediction → /liver (10 inputs)
- Parkinson's Disease Prediction → /parkinsons (8 vocal biomarkers)
- Breast Cancer Prediction → /bcancer (22 tissue measurements)
- Kidney Disease Detection → /kidney (CT scan image upload)
- Lung Disease Detection → /lung (chest X-ray upload)
- Brain Tumor Detection → /brain (MRI image upload)
- First Aid Guide → /precautions
- All Services → /services

YOUR ROLE:
- Answer health and medical questions with accurate, educational information.
- When a user asks about a disease covered by NeuralMed, mention the relevant prediction tool and its URL.
- When asked about website navigation or services, describe the tools above and their URLs.
- Be concise (under 180 words) and use plain language.
- Never diagnose or prescribe — educate only.
- Always end medical answers with a one-line reminder to consult a healthcare professional.

User message: {user_msg}"""
    reply = None
    for attempt in range(2):
        try:
            resp = text_model.generate_content(system_prompt)
            reply = (resp.text or "").strip().replace("**", "").replace("*", "")
            break
        except Exception as e:
            err = str(e)
            if attempt == 1:
                if "quota" in err.lower() or "429" in err:
                    reply = "I'm temporarily unavailable due to API rate limits. Please try again in a moment."
                else:
                    reply = f"I hit a temporary issue ({err[:80]}). Please try again."
    return jsonify({"reply": reply or "No response received. Please try again."})


# ── Doctor Portal ─────────────────────────────────────────────────────────────

def _load_model_direct(rel_path: str):
    p = ROOT_DIR / rel_path
    with open(p, "rb") as f:
        return pickle.load(f)


def _feature_importance_list(model, feature_names: list) -> list:
    try:
        if hasattr(model, 'feature_importances_'):
            vals = np.array(model.feature_importances_, dtype=float)
        elif hasattr(model, 'coef_'):
            vals = np.abs(np.array(model.coef_[0], dtype=float))
        else:
            return []
        total = vals.sum() or 1.0
        items = [{"name": n, "pct": round(float(v / total) * 100, 1)}
                 for n, v in zip(feature_names, vals)]
        return sorted(items, key=lambda x: x["pct"], reverse=True)
    except Exception:
        return []


def _clinical_ai_summary(disease: str, inputs: dict, prediction: str, confidence: float) -> str:
    prmp = f"""You are an AI clinical decision support system assisting a physician.

Disease Being Assessed: {disease}
Model Prediction: {prediction}
Model Confidence: {confidence:.1f}%
Clinical Inputs:
{chr(10).join(f'  {k}: {v}' for k, v in inputs.items())}

Write a concise clinical decision support summary. Use plain text with these exact headers (no asterisks, no bullets):

Clinical Interpretation:
Key Risk Factors:
Recommended Next Steps:
Important Caveats:

2-3 sentences per section. Use clinical terminology appropriate for a physician. This is a decision support tool, not a diagnosis."""
    try:
        resp = text_model.generate_content(prmp)
        return (resp.text or "").replace("**", "").replace("*", "—").strip()
    except Exception as e:
        err = str(e)
        if "quota" in err.lower() or "429" in err:
            return "Clinical AI summary temporarily unavailable (API rate limit). Please try again shortly."
        return f"Clinical AI summary unavailable: {err[:120]}"


@app.route('/doctor')
def doctor_portal():
    return render_template('doctor_portal.html')


@app.route('/doctor/diabetes', methods=['GET', 'POST'])
def doctor_diabetes():
    if request.method != 'POST':
        return render_template('doctor_diabetes.html')
    try:
        inputs = {
            'Pregnancies': request.form.get('pregnancies', ''),
            'Glucose (mg/dL)': request.form.get('Glucose', ''),
            'Blood Pressure (mmHg)': request.form.get('BloodPressure', ''),
            'Skin Thickness (mm)': request.form.get('skin_thickness', ''),
            'Insulin (μU/mL)': request.form.get('insulin', ''),
            'BMI': request.form.get('BMI', ''),
            'Diabetes Pedigree Function': request.form.get('DiabetesPedigreeFunction', ''),
            'Age (years)': request.form.get('Age', ''),
        }
        data = Diabetes_Data(
            pregnancies=inputs['Pregnancies'], Glucose=inputs['Glucose (mg/dL)'],
            BloodPressure=inputs['Blood Pressure (mmHg)'],
            skin_thickness=inputs['Skin Thickness (mm)'],
            insulin=inputs['Insulin (μU/mL)'], BMI=inputs['BMI'],
            DiabetesPedigreeFunction=inputs['Diabetes Pedigree Function'],
            Age=inputs['Age (years)'])
        final_data = data.get_data_as_dataframe()
        preprocessor = _load_model_direct("Artifacts/Diabetes_Disease/Diabetes_Preprocessor.pkl")
        model = _load_model_direct("Artifacts/Diabetes_Disease/Diabetes_Model.pkl")
        scaled = preprocessor.transform(final_data)
        pred = int(model.predict(scaled)[0])
        proba = model.predict_proba(scaled)[0]
        confidence = round(float(proba[pred]) * 100, 1)
        positive = pred == 1
        prediction_label = "Diabetes Detected" if positive else "No Diabetes Detected"
        feature_names = ['Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness',
                         'Insulin', 'BMI', 'Pedigree Fn', 'Age']
        importances = _feature_importance_list(model, feature_names)
        summary = _clinical_ai_summary("Diabetes Mellitus", inputs, prediction_label, confidence)
        return render_template('doctor_diabetes.html', prediction=prediction_label,
                               positive=positive, confidence=confidence,
                               importances=importances, summary=summary, inputs=inputs)
    except Exception as e:
        return render_template('doctor_diabetes.html', error=str(e))


@app.route('/doctor/heart', methods=['GET', 'POST'])
def doctor_heart():
    if request.method != 'POST':
        return render_template('doctor_heart.html')
    try:
        cp_labels = ['Typical Angina', 'Atypical Angina', 'Non-Anginal Pain', 'Asymptomatic']
        ecg_labels = ['Normal', 'ST-T Abnormality', 'LVH']
        slope_labels = ['Upsloping', 'Flat', 'Downsloping']
        thal_labels = ['Normal', 'Fixed Defect', 'Reversible Defect']
        inputs = {
            'Age (years)': request.form.get('age', ''),
            'Sex': 'Male' if request.form.get('sex') == '1' else 'Female',
            'Chest Pain Type': cp_labels[int(request.form.get('cp', 0))],
            'Resting BP (mmHg)': request.form.get('trestbps', ''),
            'Cholesterol (mg/dL)': request.form.get('chol', ''),
            'Fasting BS >120 mg/dL': 'Yes' if request.form.get('fbs') == '1' else 'No',
            'Resting ECG': ecg_labels[int(request.form.get('restecg', 0))],
            'Max Heart Rate (bpm)': request.form.get('thalach', ''),
            'Exercise-Induced Angina': 'Yes' if request.form.get('exang') == '1' else 'No',
            'ST Depression': request.form.get('oldpeak', ''),
            'ST Slope': slope_labels[int(request.form.get('slope', 0))],
            'Major Vessels (0–4)': request.form.get('ca', ''),
            'Thalassemia': thal_labels[int(request.form.get('thal', 0))],
        }
        data = CustomData(
            age=request.form.get('age'), sex=request.form.get('sex'),
            cp=request.form.get('cp'), trestbps=request.form.get('trestbps'),
            chol=request.form.get('chol'), fbs=request.form.get('fbs'),
            restecg=request.form.get('restecg'), thalach=request.form.get('thalach'),
            exang=request.form.get('exang'), oldpeak=request.form.get('oldpeak'),
            slope=request.form.get('slope'), ca=request.form.get('ca'),
            thal=request.form.get('thal'))
        final_data = data.get_data_as_dataframe()
        preprocessor = _load_model_direct("Artifacts/Heart_Disease/Heart_Preprocessor.pkl")
        model = _load_model_direct("Artifacts/Heart_Disease/Heart_Model.pkl")
        scaled = preprocessor.transform(final_data)
        pred = int(model.predict(scaled)[0])
        proba = model.predict_proba(scaled)[0]
        confidence = round(float(proba[pred]) * 100, 1)
        positive = pred == 1
        prediction_label = "Heart Disease Detected" if positive else "No Heart Disease Detected"
        feature_names = ['Age', 'Sex', 'Chest Pain', 'Resting BP', 'Cholesterol',
                         'Fasting BS', 'ECG', 'Max HR', 'Ex. Angina',
                         'ST Depress.', 'ST Slope', 'Vessels', 'Thalassemia']
        importances = _feature_importance_list(model, feature_names)
        summary = _clinical_ai_summary("Heart Disease", inputs, prediction_label, confidence)
        return render_template('doctor_heart.html', prediction=prediction_label,
                               positive=positive, confidence=confidence,
                               importances=importances, summary=summary, inputs=inputs)
    except Exception as e:
        return render_template('doctor_heart.html', error=str(e))


@app.route('/doctor/liver', methods=['GET', 'POST'])
def doctor_liver():
    if request.method != 'POST':
        return render_template('doctor_liver.html')
    try:
        inputs = {
            'Age (years)': request.form.get('age', ''),
            'Gender': 'Male' if request.form.get('gender') == '1' else 'Female',
            'Total Bilirubin (mg/dL)': request.form.get('total_bilirubin', ''),
            'Direct Bilirubin (mg/dL)': request.form.get('direct_bilirubin', ''),
            'Alkaline Phosphatase (IU/L)': request.form.get('alkaline_phosphotase', ''),
            'ALT / SGPT (IU/L)': request.form.get('alamine_aminotransferase', ''),
            'AST / SGOT (IU/L)': request.form.get('aspartate_aminotransferase', ''),
            'Total Proteins (g/dL)': request.form.get('total_proteins', ''),
            'Albumin (g/dL)': request.form.get('albumin', ''),
            'Albumin/Globulin Ratio': request.form.get('albumin_globulin_ratio', ''),
        }
        features = np.array([
            float(inputs['Age (years)']), float(request.form.get('gender', 0)),
            float(inputs['Total Bilirubin (mg/dL)']), float(inputs['Direct Bilirubin (mg/dL)']),
            float(inputs['Alkaline Phosphatase (IU/L)']), float(inputs['ALT / SGPT (IU/L)']),
            float(inputs['AST / SGOT (IU/L)']), float(inputs['Total Proteins (g/dL)']),
            float(inputs['Albumin (g/dL)']), float(inputs['Albumin/Globulin Ratio']),
        ]).reshape(1, -1)
        model = get_liver_model()
        pred = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
        positive = pred == 1
        confidence = round(float(proba[min(pred, len(proba)-1)]) * 100, 1)
        prediction_label = "Liver Disease Positive" if positive else "Liver Disease Negative"
        feature_names = ['Age', 'Gender', 'Total Bilirubin', 'Direct Bilirubin',
                         'Alk. Phosphatase', 'ALT', 'AST',
                         'Total Proteins', 'Albumin', 'A/G Ratio']
        importances = _feature_importance_list(model, feature_names)
        summary = _clinical_ai_summary("Liver Disease", inputs, prediction_label, confidence)
        return render_template('doctor_liver.html', prediction=prediction_label,
                               positive=positive, confidence=confidence,
                               importances=importances, summary=summary, inputs=inputs)
    except Exception as e:
        return render_template('doctor_liver.html', error=str(e))


@app.route('/doctor/parkinsons', methods=['GET', 'POST'])
def doctor_parkinsons():
    if request.method != 'POST':
        return render_template('doctor_parkinsons.html')
    try:
        inputs = {
            'MDVP:Fo — Avg Vocal Freq (Hz)': request.form.get('MDVPFO', ''),
            'MDVP:Fhi — Max Vocal Freq (Hz)': request.form.get('MDVPFHI', ''),
            'MDVP:Flo — Min Vocal Freq (Hz)': request.form.get('MDVPFLO', ''),
            'MDVP:Jitter — Freq Variation (%)': request.form.get('MDVPJ', ''),
            'RPDE — Recurrence Period Density': request.form.get('RPDE', ''),
            'DFA — Signal Fractal Scaling': request.form.get('DFA', ''),
            'spread2 — Nonlinear Measure': request.form.get('spread2', ''),
            'D2 — Correlation Dimension': request.form.get('D2', ''),
        }
        data = Parkinsons_Data(
            MDVPFO=float(inputs['MDVP:Fo — Avg Vocal Freq (Hz)']),
            MDVPFHI=float(inputs['MDVP:Fhi — Max Vocal Freq (Hz)']),
            MDVPFLO=float(inputs['MDVP:Flo — Min Vocal Freq (Hz)']),
            MDVPJ=float(inputs['MDVP:Jitter — Freq Variation (%)']),
            RPDE=float(inputs['RPDE — Recurrence Period Density']),
            DFA=float(inputs['DFA — Signal Fractal Scaling']),
            spread2=float(inputs['spread2 — Nonlinear Measure']),
            D2=float(inputs['D2 — Correlation Dimension']))
        final_data = data.get_data_as_dataframe()
        model = _load_model_direct("Artifacts/Parkinsons_Disease/Parkinsons_Model.pkl")
        pred = int(model.predict(final_data)[0])
        proba = model.predict_proba(final_data)[0]
        confidence = round(float(proba[pred]) * 100, 1)
        positive = pred == 1
        prediction_label = "Parkinson's Detected" if positive else "No Parkinson's Detected"
        feature_names = ['Avg Freq', 'Max Freq', 'Min Freq', 'Jitter%', 'RPDE', 'DFA', 'spread2', 'D2']
        importances = _feature_importance_list(model, feature_names)
        summary = _clinical_ai_summary("Parkinson's Disease", inputs, prediction_label, confidence)
        return render_template('doctor_parkinsons.html', prediction=prediction_label,
                               positive=positive, confidence=confidence,
                               importances=importances, summary=summary, inputs=inputs)
    except Exception as e:
        return render_template('doctor_parkinsons.html', error=str(e))


@app.route('/doctor/bcancer', methods=['GET', 'POST'])
def doctor_bcancer():
    if request.method != 'POST':
        return render_template('doctor_bcancer.html')
    try:
        inputs = {
            'Mean Texture': request.form.get('texture_mean', ''),
            'Mean Smoothness': request.form.get('smoothness_mean', ''),
            'Mean Compactness': request.form.get('compactness_mean', ''),
            'Mean Concave Points': request.form.get('concave_points_mean', ''),
            'Mean Symmetry': request.form.get('symmetry_mean', ''),
            'Mean Fractal Dimension': request.form.get('fractal_dimension_mean', ''),
            'SE Texture': request.form.get('texture_se', ''),
            'SE Area': request.form.get('area_se', ''),
            'SE Smoothness': request.form.get('smoothness_se', ''),
            'SE Compactness': request.form.get('compactness_se', ''),
            'SE Concavity': request.form.get('concavity_se', ''),
            'SE Concave Points': request.form.get('concave_points_se', ''),
            'SE Symmetry': request.form.get('symmetry_se', ''),
            'SE Fractal Dimension': request.form.get('fractal_dimension_se', ''),
            'Worst Texture': request.form.get('texture_worst', ''),
            'Worst Area': request.form.get('area_worst', ''),
            'Worst Smoothness': request.form.get('smoothness_worst', ''),
            'Worst Compactness': request.form.get('compactness_worst', ''),
            'Worst Concavity': request.form.get('concavity_worst', ''),
            'Worst Concave Points': request.form.get('concave_points_worst', ''),
            'Worst Symmetry': request.form.get('symmetry_worst', ''),
            'Worst Fractal Dimension': request.form.get('fractal_dimension_worst', ''),
        }
        data = BCancer_Data(
            texture_mean=float(inputs['Mean Texture']),
            smoothness_mean=float(inputs['Mean Smoothness']),
            compactness_mean=float(inputs['Mean Compactness']),
            concave_points_mean=float(inputs['Mean Concave Points']),
            symmetry_mean=float(inputs['Mean Symmetry']),
            fractal_dimension_mean=float(inputs['Mean Fractal Dimension']),
            texture_se=float(inputs['SE Texture']),
            area_se=float(inputs['SE Area']),
            smoothness_se=float(inputs['SE Smoothness']),
            compactness_se=float(inputs['SE Compactness']),
            concavity_se=float(inputs['SE Concavity']),
            concave_points_se=float(inputs['SE Concave Points']),
            symmetry_se=float(inputs['SE Symmetry']),
            fractal_dimension_se=float(inputs['SE Fractal Dimension']),
            texture_worst=float(inputs['Worst Texture']),
            area_worst=float(inputs['Worst Area']),
            smoothness_worst=float(inputs['Worst Smoothness']),
            compactness_worst=float(inputs['Worst Compactness']),
            concavity_worst=float(inputs['Worst Concavity']),
            concave_points_worst=float(inputs['Worst Concave Points']),
            symmetry_worst=float(inputs['Worst Symmetry']),
            fractal_dimension_worst=float(inputs['Worst Fractal Dimension']))
        final_data = data.get_data_as_dataframe()
        model = _load_model_direct("Artifacts/Breast_Cancer_Disease/BCancer_Model.pkl")
        pred = int(model.predict(final_data)[0])
        proba = model.predict_proba(final_data)[0]
        # 0=Malignant, 1=Benign
        positive = pred == 0
        confidence = round(float(proba[pred]) * 100, 1)
        prediction_label = "Malignant — Cancer Detected" if positive else "Benign — No Cancer Detected"
        feature_names = [
            'Mean Texture', 'Mean Smoothness', 'Mean Compactness', 'Mean Concave Pts',
            'Mean Symmetry', 'Mean Fractal Dim', 'SE Texture', 'SE Area',
            'SE Smoothness', 'SE Compactness', 'SE Concavity', 'SE Concave Pts',
            'SE Symmetry', 'SE Fractal Dim', 'Worst Texture', 'Worst Area',
            'Worst Smoothness', 'Worst Compactness', 'Worst Concavity', 'Worst Concave Pts',
            'Worst Symmetry', 'Worst Fractal Dim']
        importances = _feature_importance_list(model, feature_names)[:10]
        summary = _clinical_ai_summary("Breast Cancer", inputs, prediction_label, confidence)
        return render_template('doctor_bcancer.html', prediction=prediction_label,
                               positive=positive, confidence=confidence,
                               importances=importances, summary=summary, inputs=inputs)
    except Exception as e:
        return render_template('doctor_bcancer.html', error=str(e))


if __name__ == '__main__':
    # 5000 is often taken on macOS (e.g. AirPlay Receiver); override with FLASK_RUN_PORT or PORT
    _port = int(os.environ.get("FLASK_RUN_PORT") or os.environ.get("PORT") or "5001")
    app.run(debug=True, host="0.0.0.0", port=_port)