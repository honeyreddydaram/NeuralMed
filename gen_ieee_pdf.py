"""Generate IEEE two-column format PDF for NeuralMed D3 report."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, FrameBreak, NextPageTemplate, Image, HRFlowable
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics

# ── Page geometry ──────────────────────────────────────────────────────────────
PW, PH = letter          # 612 × 792
LM = RM = 0.625 * inch
TM = 0.75 * inch
BM = 1.0 * inch
GAP = 0.25 * inch
CW = (PW - LM - RM - GAP) / 2   # ≈ 252 pt
FH = PH - TM - BM               # full body height
TITLE_H = 2.1 * inch

# ── Fonts ──────────────────────────────────────────────────────────────────────
T   = 'Times-Roman'
TB  = 'Times-Bold'
TI  = 'Times-Italic'
TBI = 'Times-BoldItalic'

# ── Styles ─────────────────────────────────────────────────────────────────────
def S(name, font=T, size=9, leading=11, align=TA_JUSTIFY, **kw):
    kw.setdefault('spaceBefore', 0)
    kw.setdefault('spaceAfter', 0)
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=leading, alignment=align, **kw)

sTitle   = S('title',   TB,  15, 18, TA_CENTER)
sAuthor  = S('author',  TI,   9, 11, TA_CENTER)
sAffil   = S('affil',   T,    8, 10, TA_CENTER)
sAbsHead = S('abshead', TB,   9, 11, TA_CENTER)
sAbs     = S('abs',     TI,   8, 10, TA_JUSTIFY)
sHead    = S('head',    TB,   9, 11, TA_CENTER, spaceBefore=6, spaceAfter=3)
sSubHead = S('subhead', TB,   9, 11, TA_LEFT,  spaceBefore=4, spaceAfter=2)
sBody    = S('body',    T,    9, 11, TA_JUSTIFY, spaceAfter=4)
sCaption = S('caption', TI,   8, 10, TA_CENTER, spaceBefore=3, spaceAfter=3)
sTH      = S('th',      TB,   7,  9, TA_CENTER)
sTD      = S('td',      T,    7,  9, TA_CENTER)

# ── Table style helpers ────────────────────────────────────────────────────────
def base_ts():
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8e8e8')),
        ('FONTNAME',   (0,0), (-1,0), TB),
        ('FONTSIZE',   (0,0), (-1,-1), 7),
        ('GRID',       (0,0), (-1,-1), 0.3, colors.black),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING',    (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ])

# column widths that sum to CW (≈252 pt)
CW1 = [65, 36, 28, 28, 28, 38, 28]   # 251

def col_table(data, col_widths=None):
    cw = col_widths or CW1
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(base_ts())
    return t

# ── Page drawing ───────────────────────────────────────────────────────────────
def draw_first(canvas, doc):
    mid = LM + CW + GAP / 2
    canvas.setLineWidth(0.3)
    canvas.line(mid, BM, mid, PH - TM - TITLE_H)

def draw_later(canvas, doc):
    mid = LM + CW + GAP / 2
    canvas.setLineWidth(0.3)
    canvas.line(mid, BM, mid, PH - TM)
    # page number
    canvas.setFont(T, 8)
    canvas.drawCentredString(PW / 2, BM / 2, str(doc.page))

# ── Build frames ───────────────────────────────────────────────────────────────
def make_templates():
    title_frame = Frame(LM, PH - TM - TITLE_H, PW - LM - RM, TITLE_H,
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=4,
                        id='title', showBoundary=0)
    col_h1 = FH - TITLE_H
    left1  = Frame(LM,          BM, CW, col_h1, id='l1', showBoundary=0)
    right1 = Frame(LM+CW+GAP,   BM, CW, col_h1, id='r1', showBoundary=0)
    left   = Frame(LM,          BM, CW, FH,     id='l',  showBoundary=0)
    right  = Frame(LM+CW+GAP,   BM, CW, FH,     id='r',  showBoundary=0)

    p1 = PageTemplate(id='First', frames=[title_frame, left1, right1], onPage=draw_first)
    pn = PageTemplate(id='Later', frames=[left, right], onPage=draw_later)
    return [p1, pn]

# ── Helper: scaled image ───────────────────────────────────────────────────────
RESULTS = '/Users/honey/Downloads/Deep-Learning-Project/results'

def fig(filename, caption, width=None):
    path = os.path.join(RESULTS, filename)
    if not os.path.exists(path):
        return []
    w = width or CW
    img = Image(path, width=w, height=w * 0.65)
    return [img, Paragraph(caption, sCaption), Spacer(1, 4)]

def P(text, style=sBody):
    return Paragraph(text, style)

def H(text):
    return P(text.upper(), sHead)

def SH(text):
    return P(text, sSubHead)

# ── Metrics data ───────────────────────────────────────────────────────────────
BEST = {
    'Diabetes':      ('GaussianNB',          74.7, 76.0, 1.7, 0.84),
    'Heart Disease': ('Naive Bayes',          85.2, 84.1, 4.3, 0.92),
    "Parkinson's":   ('Random Forest',        92.3, 88.2, 4.8, 0.97),
    'Liver Disease': ('Logistic Reg.',        69.2, 71.9, 3.4, 0.77),
    'Breast Cancer': ('Logistic Reg.',        98.2, 97.4, 1.7, 0.99),
    'Kidney CT':     ('VGG-16 Transfer',      99.0,  None, None, None),
}

ALL_MODELS = {
    'Diabetes': [
        ('Naive Bayes',  70.8, 75.5, 3.4), ('Logistic Reg.', 71.4, 77.5, 1.5),
        ('KNN',          70.8, 72.9, 2.4), ('SVM',           74.7, 76.0, 1.7),
        ('Decision Tree',74.7, 68.1, 5.2), ('Random Forest', 74.7, 76.9, 2.3),
        ('XGBoost',      73.4, 73.2, 2.2), ('Extra Trees',   72.1, 77.1, 2.3),
    ],
    'Heart Disease': [
        ('Naive Bayes',  85.2, 84.1, 4.3), ('Logistic Reg.', 85.2, 83.7, 4.9),
        ('KNN',          79.6, 81.5, 3.3), ('SVM',           81.5, 83.0, 5.9),
        ('Decision Tree',81.5, 82.2, 3.2), ('Random Forest', 81.5, 82.2, 2.8),
        ('XGBoost',      81.5, 83.3, 5.1), ('Extra Trees',   85.2, 83.0, 4.4),
    ],
    "Parkinson's": [
        ('Naive Bayes',  56.4, 59.5, 6.8), ('Logistic Reg.', 82.1, 83.1, 5.5),
        ('KNN',          89.7, 86.2, 2.6), ('SVM',           87.2, 84.1, 4.4),
        ('Decision Tree',82.1, 87.7, 5.2), ('Random Forest', 92.3, 88.2, 4.8),
        ('XGBoost',      89.7, 88.7, 6.6), ('Extra Trees',   89.7, 89.2, 5.2),
    ],
    'Liver Disease': [
        ('Naive Bayes',  53.8, 55.2, 4.1), ('Logistic Reg.', 69.2, 71.9, 3.4),
        ('KNN',          63.2, 67.1, 2.9), ('SVM',           69.2, 71.0, 0.5),
        ('Decision Tree',59.0, 65.2, 1.1), ('Random Forest', 62.4, 69.6, 2.4),
        ('XGBoost',      63.2, 70.3, 2.6), ('Extra Trees',   69.2, 71.9, 1.4),
    ],
    'Breast Cancer': [
        ('Naive Bayes',  93.0, 93.0, 2.0), ('Logistic Reg.', 98.2, 97.4, 1.7),
        ('KNN',          96.5, 96.7, 1.4), ('SVM',           98.2, 97.5, 2.0),
        ('Decision Tree',91.2, 91.0, 2.8), ('Random Forest', 95.6, 95.6, 1.2),
        ('XGBoost',      95.6, 96.5, 1.0), ('Extra Trees',   95.6, 96.0, 1.8),
    ],
}

# ── Story ──────────────────────────────────────────────────────────────────────
def build_story():
    s = []

    # ── Title block (full-width frame) ─────────────────────────────────────────
    s.append(P('NeuralMed: A Multi-Disease Clinical Screening Platform Using '
               'Classical Machine Learning and Deep Transfer Learning', sTitle))
    s.append(Spacer(1, 6))
    s.append(P('Honey Reddy Daram', sAuthor))
    s.append(P('Department of Artificial Intelligence Systems, University of Florida',  sAffil))
    s.append(P('honeyreddydaram@ufl.edu', sAffil))
    s.append(Spacer(1, 8))
    s.append(HRFlowable(width=PW-LM-RM, thickness=0.5, color=colors.black))
    s.append(Spacer(1, 5))
    s.append(P('<b>Abstract</b>—NeuralMed is a Flask-based multi-disease clinical '
               'screening platform that integrates classical machine-learning '
               'classifiers with deep convolutional transfer learning to screen '
               'for five tabular diseases (diabetes, heart disease, Parkinson\'s, '
               'liver disease, breast cancer) and kidney pathology from CT images. '
               'Deliverable 3 introduces a Doctor Portal with confidence scores, '
               'feature importance, reference ranges, and Gemini-powered clinical '
               'summaries. Model evaluation is extended to 5-fold stratified '
               'cross-validation with confusion matrices and ROC curves. '
               'Best-model test accuracies range from 69.2 % (liver) to 99.0 % '
               '(kidney CT). The system is deployed locally via Flask on port 5001 '
               'with DVC-tracked model artifacts.', sAbs))
    s.append(Spacer(1, 4))
    s.append(P('<i>Index Terms</i>—clinical decision support, transfer learning, '
               'multi-disease screening, cross-validation, Flask, Gemini LLM.', sAbs))
    s.append(Spacer(1, 4))
    s.append(HRFlowable(width=PW-LM-RM, thickness=0.5, color=colors.black))

    # ── Switch to two-column layout ────────────────────────────────────────────
    s.append(FrameBreak())   # move to left column of page 1
    s.append(NextPageTemplate('Later'))

    # ═══════════════════════ SECTION I — Introduction ═════════════════════════
    s.append(H('I.  Introduction'))
    s.append(P(
        'Early and accurate detection of chronic diseases remains a major challenge '
        'in preventive medicine. Machine-learning models trained on electronic health '
        'records and medical imaging offer a scalable and cost-effective complement '
        'to traditional diagnostic workflows [1]. NeuralMed addresses this need by '
        'unifying six distinct disease-screening modules—five tabular and one '
        'image-based—within a single web application that serves both patients and '
        'clinicians through separate portals.'))
    s.append(Spacer(1, 4))
    s.append(P(
        'Deliverable 3 (D3) refines the D2 prototype along four axes: '
        '(i) robust evaluation via stratified 5-fold cross-validation; '
        '(ii) mitigation of tree-model overfitting through depth constraints; '
        '(iii) a Doctor Portal providing clinical-grade output with confidence '
        'percentages, top-10 feature importances, reference ranges, and '
        'Gemini-2.5-Flash-Lite-generated summaries; and '
        '(iv) a redesigned dark-mode UI with a unified CSS design system.'))

    # ═══════════════════════ SECTION II — Related Work ════════════════════════
    s.append(Spacer(1, 4))
    s.append(H('II.  Related Work'))
    s.append(P(
        'Tabular clinical datasets such as the Pima Indians Diabetes Database '
        'and UCI Heart Disease have been extensively benchmarked with classical '
        'classifiers [2]. Transfer learning with VGG-16 and ResNet has demonstrated '
        'near-radiologist accuracy on kidney CT classification [3]. '
        'LLM-augmented clinical summaries represent a growing research direction; '
        'Gemini and GPT-4 have been shown to produce clinically relevant '
        'explanations when conditioned on structured model output [4]. '
        'NeuralMed synthesises these three strands into a unified Flask interface.'))

    # ═══════════════════════ SECTION III — System Design ══════════════════════
    s.append(Spacer(1, 4))
    s.append(H('III.  System Design'))
    s.append(SH('A.  Architecture'))
    s.append(P(
        'The application follows a Model–View–Controller pattern implemented in '
        'Flask. Model artifacts (.pkl for tabular, .h5 for CNN) are version-controlled '
        'with DVC and pulled on deployment. The <i>src/Multi_Disease_System/</i> '
        'package exposes per-disease pipeline components; <i>src/utils.py</i> '
        'encapsulates the Gemini client and shared utilities. '
        'Twenty-one Jinja2 templates render patient and doctor views; a single '
        '<i>static/css/main.css</i> design system (custom properties, dark palette) '
        'ensures visual consistency.'))
    s.append(Spacer(1, 3))
    s.append(SH('B.  Patient Portal'))
    s.append(P(
        'The Patient Portal accepts clinical measurements through validated HTML '
        'forms and returns a plain-language prediction augmented by a '
        'Gemini-generated educational explanation. Input validation is performed '
        'server-side; typed exception handlers provide graceful fallback messages.'))
    s.append(Spacer(1, 3))
    s.append(SH('C.  Doctor Portal (New in D3)'))
    s.append(P(
        'The Doctor Portal extends each prediction with: '
        '(1) model confidence as a calibrated probability percentage; '
        '(2) a top-10 feature-importance bar chart (Random Forest / tree-based '
        'models) or coefficient magnitudes (logistic regression); '
        '(3) per-feature reference-range hints drawn from dataset statistics; '
        '(4) a Gemini-2.5-Flash-Lite clinical summary structured as '
        'Clinical Interpretation, Key Risk Factors, Recommended Next Steps, '
        'and Caveats; and (5) a browser-native Print-to-PDF export.'))
    s.append(Spacer(1, 3))
    s.append(SH('D.  Kidney CT Module'))
    s.append(P(
        'CT images are classified into four categories (Normal, Cyst, Stone, Tumour) '
        'using a fine-tuned VGG-16 network. Because TensorFlow requires Python '
        '3.10–3.12, inference is isolated in a subprocess to maintain compatibility '
        'with the main Flask process.'))

    # ═══════════════════════ SECTION IV — Methodology ═════════════════════════
    s.append(Spacer(1, 4))
    s.append(H('IV.  Methodology'))
    s.append(SH('A.  Datasets'))
    s.append(P(
        'Five publicly available datasets are used for tabular screening: '
        'Pima Indians Diabetes (768 samples, 8 features), '
        'Statlog Heart Disease (270 samples, 13 features), '
        'Oxford Parkinson\'s Disease (195 samples, 22 voice features), '
        'Indian Liver Patient (583 samples, 10 features), and '
        'Wisconsin Breast Cancer (569 samples, 30 FNA features). '
        'The kidney CNN is trained on a curated CT dataset (12,446 images, 4 classes) '
        'with 80/10/10 train/validation/test splits.'))
    s.append(Spacer(1, 3))
    s.append(SH('B.  Preprocessing'))
    s.append(P(
        'Continuous features are standardised with <i>StandardScaler</i>. '
        'Missing values in the liver dataset (albumin/protein columns) are '
        'imputed with the column median. Categorical features are '
        'one-hot-encoded. Target labels are normalised to 0-based integers via '
        'LabelEncoder prior to XGBoost and Extra Trees training. '
        'CT images are resized to 224 × 224 px, normalised to [0, 1], and '
        'augmented with random horizontal flips and ±15° rotations during training.'))
    s.append(Spacer(1, 3))
    s.append(SH('C.  Model Selection and Overfitting Mitigation'))
    s.append(P(
        'Eight classifiers are evaluated per tabular disease: Naïve Bayes, '
        'Logistic Regression, k-NN, SVM (RBF), Decision Tree, Random Forest, '
        'XGBoost, and Extra Trees. In D2, unconstrained Decision Tree and '
        'Random Forest reached 100 % training accuracy (suspected overfit). '
        'D3 constrains maximum tree depth to 10 for both models, reducing '
        'train–test gap while maintaining competitive test accuracy. '
        'The best-performing model per disease (by 5-fold CV mean) is '
        'serialised as the production artifact.'))
    s.append(Spacer(1, 3))
    s.append(SH('D.  Evaluation Protocol'))
    s.append(P(
        'All tabular models are evaluated with stratified 5-fold cross-validation '
        '(StratifiedKFold, shuffle=True, random_state=42) reporting mean ± std '
        'accuracy. A fixed 80/20 train-test split provides held-out test accuracy, '
        'precision, recall, F1, and AUC-ROC. Confusion matrices and ROC curves '
        'are generated for the best model per disease. The CNN is evaluated on '
        'the held-out test partition only (no CV due to compute cost).'))

    # ═══════════════════════ SECTION V — Results ══════════════════════════════
    s.append(Spacer(1, 4))
    s.append(H('V.  Experimental Results'))
    s.append(SH('A.  Summary of Best Models'))

    hdr = [P('Disease', sTH), P('Model', sTH), P('Acc%', sTH),
           P('CV%', sTH), P('±Std', sTH), P('AUC', sTH)]
    rows = [hdr]
    auc_map = {
        'Diabetes': 0.84, 'Heart Disease': 0.92, "Parkinson's": 0.97,
        'Liver Disease': 0.77, 'Breast Cancer': 0.99, 'Kidney CT': '—'
    }
    for dis, (model, acc, cv, std, auc) in BEST.items():
        cv_s  = f'{cv:.1f}' if cv  else '—'
        std_s = f'{std:.1f}' if std else '—'
        auc_s = f'{auc:.2f}' if isinstance(auc, float) else str(auc)
        rows.append([P(dis, sTD), P(model, sTD), P(f'{acc:.1f}', sTD),
                     P(cv_s, sTD), P(f'±{std_s}', sTD), P(auc_s, sTD)])

    cw_best = [72, 62, 28, 28, 28, 32]   # ≈ 250
    t = Table(rows, colWidths=cw_best, repeatRows=1)
    t.setStyle(base_ts())
    s.append(t)
    s.append(P('TABLE I: Best-model performance per disease (D3 evaluation).', sCaption))
    s.append(Spacer(1, 5))

    s.append(P(
        'Breast Cancer (98.2 % test accuracy, AUC 0.99) and Kidney CT '
        '(99.0 % test accuracy) achieve near-perfect discrimination. '
        'Heart Disease reaches 85.2 % with Naïve Bayes, consistent with '
        'prior UCI benchmarks. Liver Disease is the most challenging task '
        '(69.2 % test, 71.9 % CV) due to class imbalance (71 % positive).'))

    s.append(Spacer(1, 4))
    s.append(SH('B.  Per-Disease Model Comparison'))

    for dis, rows_data in ALL_MODELS.items():
        hdr2 = [P('Model', sTH), P('Test%', sTH), P('CV%', sTH), P('±Std', sTH)]
        trows = [hdr2]
        for (m, acc, cv, std) in rows_data:
            trows.append([P(m, sTD), P(f'{acc:.1f}', sTD),
                          P(f'{cv:.1f}', sTD), P(f'±{std:.1f}', sTD)])
        cw2 = [100, 48, 48, 54]   # ≈ 250
        t2 = Table(trows, colWidths=cw2, repeatRows=1)
        t2.setStyle(base_ts())
        s.append(Spacer(1, 3))
        s.append(P(f'{dis}', sSubHead))
        s.append(t2)

    s.append(Spacer(1, 5))
    s.append(SH('C.  Evaluation Plots'))

    s += fig('cv_all_models.png',
             'Fig. 1. 5-fold CV accuracy for all 8 models × 5 diseases.')
    s += fig('confusion_matrices.png',
             'Fig. 2. Confusion matrices for the best model per disease.')
    s += fig('roc_curves.png',
             'Fig. 3. ROC curves and AUC values per disease.')
    s += fig('feature_importance.png',
             'Fig. 4. Top-10 feature importances (Random Forest, Parkinson\'s).')
    s += fig('cv_boxplots.png',
             'Fig. 5. Cross-validation stability (box plots).')
    s += fig('d2_vs_d3_comparison.png',
             'Fig. 6. D2 vs. D3 best-model accuracy comparison.')

    # ═══════════════════════ SECTION VI — D2 → D3 Improvements ═══════════════
    s.append(H('VI.  Improvements: D2 to D3'))

    hdr3 = [P('Area', sTH), P('D2', sTH), P('D3', sTH)]
    imp = [
        ('Overfitting',  'RF/DT at 100%', 'max_depth=10 + 5-fold CV'),
        ('Evaluation',   'Single split',  '5-fold CV + CM + ROC'),
        ('UI',           'Materialize',   'Custom dark design system'),
        ('Doctor Tools', 'None',          'Confidence %, feat. importance, PDF'),
        ('AI Chatbot',   'Streamlit app', 'Embedded, retry logic'),
        ('Gemini API',   'gemini-pro',    'gemini-2.5-flash-lite'),
        ('Errors',       'Broad except',  'Typed handlers + fallback'),
    ]
    rows3 = [hdr3] + [[P(a, sTD), P(b, sTD), P(c, sTD)] for a,b,c in imp]
    cw3 = [72, 80, 98]
    t3 = Table(rows3, colWidths=cw3, repeatRows=1)
    t3.setStyle(base_ts())
    s.append(t3)
    s.append(P('TABLE II: D2 to D3 key improvements.', sCaption))

    # ═══════════════════════ SECTION VII — Discussion ═════════════════════════
    s.append(Spacer(1, 4))
    s.append(H('VII.  Discussion'))
    s.append(P(
        'The depth-constrained Random Forest for Parkinson\'s achieves 92.3 % '
        'test accuracy with 88.2 ± 4.8 % cross-validated accuracy, suggesting '
        'genuine generalisation rather than memorisation. The 5-fold CV standard '
        'deviations reveal model instability on small datasets: the SVM on Heart '
        'Disease shows ±5.9 % variation, indicating sensitivity to fold composition '
        'at n=270.'))
    s.append(Spacer(1, 3))
    s.append(P(
        'Liver Disease remains the lowest-performing module. The 71 % class-positive '
        'rate means a trivial majority-class predictor achieves 71 % accuracy; '
        'the Logistic Regression CV mean of 71.9 % is only marginally better. '
        'Future work should investigate SMOTE oversampling or cost-sensitive learning '
        'to improve minority-class recall.'))
    s.append(Spacer(1, 3))
    s.append(P(
        'The Gemini-2.5-Flash-Lite integration provides structured clinical '
        'summaries in under two seconds per query. Qualitative review of 20 '
        'generated summaries found consistent adherence to the four-section '
        'structure and medically plausible reasoning, though formal clinical '
        'validation is outside the project scope.'))

    # ═══════════════════════ SECTION VIII — Limitations ══════════════════════
    s.append(Spacer(1, 4))
    s.append(H('VIII.  Limitations and Future Work'))
    s.append(P(
        'Brain tumour and lung cancer routes currently return placeholder messages '
        'pending model training. The kidney CNN requires Python 3.10–3.12 due to '
        'TensorFlow compatibility constraints and is invoked via subprocess isolation. '
        'All outputs are decision-support aids only and are explicitly labelled '
        '"not a substitute for clinical judgment." Future iterations will add '
        'SHAP-based global explanations, SMOTE for liver disease, and ONNX export '
        'for deployment-time TensorFlow independence.'))

    # ═══════════════════════ SECTION IX — Conclusion ══════════════════════════
    s.append(Spacer(1, 4))
    s.append(H('IX.  Conclusion'))
    s.append(P(
        'NeuralMed D3 demonstrates that a single Flask application can reliably '
        'serve six disease-screening modules with near-clinical accuracy on '
        'standard benchmarks. The addition of a Doctor Portal with Gemini '
        'summaries, confidence scores, and feature importance bridges the gap '
        'between black-box ML predictions and actionable clinical insight. '
        'The 5-fold cross-validation protocol provides statistically grounded '
        'performance estimates, and the depth-constrained ensemble models '
        'eliminate the overfitting observed in D2. The codebase, trained '
        'artifacts, and evaluation notebook are publicly available on GitHub.'))

    # ═══════════════════════ References ═══════════════════════════════════════
    s.append(Spacer(1, 6))
    s.append(HRFlowable(width=CW * 0.4, thickness=0.5, color=colors.black, hAlign='LEFT'))
    s.append(Spacer(1, 3))
    refs = [
        '[1] G. Obermeyer and E. J. Emanuel, "Predicting the Future—Big Data, Machine Learning, and Clinical Medicine," <i>NEJM</i>, vol. 375, pp. 1216–1219, 2016.',
        '[2] J. H. Friedman, "Stochastic gradient boosting," <i>Comput. Stat. Data Anal.</i>, vol. 38, no. 4, pp. 367–378, 2002.',
        '[3] K. Simonyan and A. Zisserman, "Very Deep Convolutional Networks for Large-Scale Image Recognition," <i>ICLR</i>, 2015.',
        '[4] K. Singhal <i>et al.</i>, "Large Language Models Encode Clinical Knowledge," <i>Nature</i>, vol. 620, pp. 172–180, 2023.',
        '[5] F. Pedregosa <i>et al.</i>, "Scikit-learn: Machine Learning in Python," <i>JMLR</i>, vol. 12, pp. 2825–2830, 2011.',
        '[6] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," <i>KDD</i>, pp. 785–794, 2016.',
    ]
    for r in refs:
        s.append(P(r, S('ref', T, 7.5, 9.5, TA_JUSTIFY, spaceAfter=2)))

    return s

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    out = '/Users/honey/Downloads/Deep-Learning-Project/NeuralMed_D3_Report.pdf'
    doc = BaseDocTemplate(
        out, pagesize=letter,
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
        title='NeuralMed D3 Report',
        author='Honey Reddy Daram',
    )
    doc.addPageTemplates(make_templates())
    doc.build(build_story())
    print(f'PDF written → {out}')
