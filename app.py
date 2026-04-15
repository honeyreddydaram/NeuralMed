import warnings
warnings.simplefilter('ignore')

import os
import pickle
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

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
            an = round(pred[0], 2)
            return render_template('bcancer.html', final_result=an)
        except:
            pass
    return render_template('bcancer.html')

@app.route('/diabetes', methods=["GET", "POST"])
def diabetes():
    if request.method == "POST":
        try:
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
            return render_template("diabetes.html", final_result=pred)
        except Exception as e:
            pass
    return render_template("diabetes.html")

@app.route('/heart', methods=["GET", "POST"])
def heart():
    if request.method == "POST":
        try:
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
            file_path = 'temp.jpg'
            file.save(file_path)
            img = cv2.imread(file_path)
            img = cv2.resize(img, (150, 150))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
            predictions = get_kidney_model().predict(img)
            prediction_label = class_labels[np.argmax(predictions)]
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
            result = round(pred[0], 2)
            return render_template("parkinson.html", final_result=result)
        except:
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
        ans = (
            "Could not generate text. Set GOOGLE_API_KEY or API_KEY in your project .env file "
            f"and ensure the Gemini API is enabled. Details: {e!s}"
        )
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

if __name__ == '__main__':
    # 5000 is often taken on macOS (e.g. AirPlay Receiver); override with FLASK_RUN_PORT or PORT
    _port = int(os.environ.get("FLASK_RUN_PORT") or os.environ.get("PORT") or "5001")
    app.run(debug=True, host="0.0.0.0", port=_port)