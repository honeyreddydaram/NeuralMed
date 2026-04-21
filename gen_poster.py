"""Generate NeuralMed 36x48 inch academic poster — dark theme."""
import os
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.pagesizes import landscape
from PIL import Image as PILImage

# ── Dimensions ─────────────────────────────────────────────────────────────────
PW = 36 * inch   # 2592 pt
PH = 48 * inch   # 3456 pt
M  = 0.45 * inch  # margin

# ── Colours ────────────────────────────────────────────────────────────────────
BG       = colors.white
PRIMARY  = colors.HexColor('#0057b8')
ACCENT   = colors.HexColor('#5c35cc')
CARD     = colors.HexColor('#f4f7fb')
BORDER   = colors.HexColor('#c5d5e8')
WHITE    = colors.HexColor('#111111')   # body text
MUTED    = colors.HexColor('#555555')
RED      = colors.HexColor('#c0392b')
GREEN    = colors.HexColor('#1a7a3e')
YELLOW   = colors.HexColor('#b35c00')

# ── Fonts ──────────────────────────────────────────────────────────────────────
T   = 'Helvetica'
TB  = 'Helvetica-Bold'
TI  = 'Helvetica-Oblique'

def S(name, font=T, size=18, leading=None, align=TA_LEFT, color=WHITE, **kw):
    kw.setdefault('spaceBefore', 0)
    kw.setdefault('spaceAfter', 0)
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=leading or size*1.25,
                          alignment=align, textColor=color, **kw)

# ── Style definitions ──────────────────────────────────────────────────────────
sMainTitle  = S('mt',  TB,  72, 82, TA_CENTER, colors.white)
sSubTitle   = S('st',  T,   32, 40, TA_CENTER, colors.HexColor('#cce0ff'))
sAuthor     = S('au',  TB,  28, 36, TA_CENTER, colors.white)
sAffil      = S('af',  T,   24, 30, TA_CENTER, colors.HexColor('#cce0ff'))

sSectHead   = S('sh',  TB,  34, 40, TA_CENTER, PRIMARY, spaceBefore=8, spaceAfter=6)
sSubHead    = S('ssh', TB,  24, 30, TA_LEFT,   PRIMARY, spaceBefore=4, spaceAfter=4)
sBody       = S('b',   T,   20, 27, TA_JUSTIFY, WHITE,  spaceAfter=5)
sBodyC      = S('bc',  T,   20, 27, TA_CENTER,  WHITE)
sBullet     = S('bu',  T,   20, 27, TA_LEFT,    WHITE,  leftIndent=18, spaceAfter=3)
sCaption    = S('cap', TI,  18, 23, TA_CENTER,  MUTED,  spaceBefore=4)
sTH         = S('th',  TB,  19, 24, TA_CENTER,  PRIMARY)
sTD         = S('td',  T,   19, 24, TA_CENTER,  WHITE)
sTDL        = S('tdl', T,   19, 24, TA_LEFT,    WHITE)
sTag        = S('tag', TB,  17, 22, TA_CENTER,  ACCENT)
sHighlight  = S('hi',  TB,  22, 28, TA_CENTER,  GREEN)

def P(text, style=sBody):    return Paragraph(text, style)
def SP(h=12):                return Spacer(1, h)
def HR(w=None, color=BORDER): return HRFlowable(width=w or '100%', thickness=1, color=color)

# ── Helpers ────────────────────────────────────────────────────────────────────
RESULTS = '/Users/honey/Downloads/Deep-Learning-Project/results'
DOCS    = '/Users/honey/Downloads/Deep-Learning-Project/docs_new'

def rimg(fname, w, base=RESULTS):
    path = os.path.join(base, fname)
    if not os.path.exists(path): return []
    with PILImage.open(path) as im: iw, ih = im.size
    return [Image(path, width=w, height=w*(ih/iw)), SP(6)]

def simg(fname, w, caption=None):
    items = rimg(fname, w, base=DOCS)
    if caption and items:
        items.append(P(caption, sCaption))
    return items

def card_table(data, col_widths, row_bg=True):
    ts = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#dce8f5')),
        ('TEXTCOLOR',     (0,0), (-1,0),  PRIMARY),
        ('FONTNAME',      (0,0), (-1,0),  TB),
        ('FONTSIZE',      (0,0), (-1,-1), 18),
        ('GRID',          (0,0), (-1,-1), 0.5, BORDER),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND',    (0,1), (-1,-1), colors.white),
    ])
    if row_bg:
        for i in range(1, len(data)):
            c = colors.HexColor('#eaf1fb') if i % 2 == 0 else colors.white
            ts.add('BACKGROUND', (0,i), (-1,i), c)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(ts)
    return t

# ── Page background ────────────────────────────────────────────────────────────
def draw_bg(canvas, doc):
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
    # top accent bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PH-10, PW, 10, fill=1, stroke=0)
    # bottom accent bar
    canvas.rect(0, 0, PW, 8, fill=1, stroke=0)

# ── Column layout helper ───────────────────────────────────────────────────────
BODY_W = PW - 2*M
COL_GAP = 0.3 * inch
COL2 = (BODY_W - COL_GAP) / 2
COL3 = (BODY_W - 2*COL_GAP) / 3

def section_box(title, content_table, width=None):
    w = width or BODY_W
    title_row = [[P(title, sSectHead)]]
    title_t = Table(title_row, colWidths=[w])
    title_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#dce8f5')),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 16),
        ('RIGHTPADDING',  (0,0), (-1,-1), 16),
        ('LINEBELOW', (0,0), (-1,-1), 2, PRIMARY),
    ]))
    return [title_t, SP(8), content_table, SP(18)]

# ── Build story ────────────────────────────────────────────────────────────────
def build():
    story = []

    # ════════════════════════════ HEADER ══════════════════════════════════════
    header_data = [[
        P('NeuralMed', sMainTitle),
        SP(6),
        P('A Multi-Disease Clinical Screening Platform Using Classical ML and Deep Transfer Learning', sSubTitle),
        SP(8),
        P('Honey Reddy Daram', sAuthor),
        P('Dept. of Artificial Intelligence Systems, University of Florida  ·  honeyreddydaram@ufl.edu', sAffil),
        SP(10),
        HR(color=PRIMARY),
    ]]
    header_t = Table([[cell] for cell in header_data[0]], colWidths=[BODY_W])
    header_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('TOPPADDING', (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,0), (-1,-1), 18),
    ]))
    story += [header_t, SP(16)]

    # ════════════════════ ROW 1: Motivation | Architecture | Algorithms ════════

    # ── Motivation ─────────────────────────────────────────────────────────────
    mot = [
        [P('Overview', sSectHead)],
        [SP(6)],
        [P('NeuralMed unifies <b>five disease-screening modules</b> and a '
           '<b>deep learning CT classifier</b> into a single Flask web application '
           'serving both patients and clinicians through dedicated portals.', sBody)],
        [SP(10)],

        [P('Patient Portal — Algorithms', sSubHead)],
        [P('→ <b>Diabetes:</b> Gaussian Naïve Bayes — probabilistic classifier '
           'optimal for continuous clinical features (glucose, BMI, insulin)', sBullet)],
        [P('→ <b>Heart Disease:</b> Naïve Bayes — strong performance on correlated '
           'cardiovascular markers (ECG, cholesterol, thalassemia)', sBullet)],
        [P("→ <b>Parkinson's:</b> Random Forest (max_depth=10) — ensemble of "
           'decision trees on 8 vocal biomarkers; depth-constrained to prevent overfitting', sBullet)],
        [P('→ <b>Breast Cancer:</b> Logistic Regression — linear separability in '
           '30-feature FNA space; 98.2% test accuracy', sBullet)],
        [P('→ <b>Kidney CT:</b> VGG-16 Transfer Learning — ImageNet pretrained CNN '
           'fine-tuned for 4-class CT classification (Normal/Cyst/Stone/Tumor)', sBullet)],
        [SP(10)],

        [P('Doctor Portal — Clinical Algorithm Outputs', sSubHead)],
        [P('→ <b>Confidence %:</b> model.predict_proba() — calibrated class probability', sBullet)],
        [P('→ <b>Feature Importance:</b> RF feature_importances_ / LR coefficients — '
           'top-10 ranked by magnitude', sBullet)],
        [P('→ <b>Reference Ranges:</b> dataset-derived benign vs. malignant thresholds '
           'displayed per input field', sBullet)],
        [P('→ <b>Gemini 2.5 Flash Lite:</b> LLM structured prompt → Clinical '
           'Interpretation · Risk Factors · Next Steps · Caveats', sBullet)],
        [SP(10)],

        [P('Evaluation Protocol', sSubHead)],
        [P('→ 8 classifiers benchmarked per disease', sBullet)],
        [P('→ Stratified 5-fold CV — mean ± std accuracy', sBullet)],
        [P('→ Held-out 80/20 split — test acc, precision, recall, F1, AUC', sBullet)],
    ]
    mot_t = Table(mot, colWidths=[COL3])
    mot_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
    ]))

    # ── Architecture ───────────────────────────────────────────────────────────
    arch_rows = [
        [P('System Architecture', sSectHead)],
        [SP(8)],
        [P('DATA INPUT', S('a1', TB, 22, 28, TA_CENTER, YELLOW))],
        [P('Tabular: 5 clinical CSV datasets  |  Image: CT scan upload', sBodyC)],
        [SP(6)],
        [P('▼', sBodyC)],
        [SP(4)],
        [P('PREPROCESSING', S('a2', TB, 22, 28, TA_CENTER, YELLOW))],
        [P('StandardScaler  ·  LabelEncoder  ·  Median imputation\n'
           'Image: Resize 224×224  ·  Normalize [0,1]  ·  Augmentation', sBodyC)],
        [SP(6)],
        [P('▼', sBodyC)],
        [SP(4)],
        [P('ALGORITHM LAYER', S('a3', TB, 22, 28, TA_CENTER, YELLOW))],
        [SP(4)],
    ]

    algo_grid = [
        [P('Disease', sTH), P('Algorithm', sTH), P('Why Chosen', sTH)],
        [P('Diabetes', sTD), P('GaussianNB', sTD),
         P('Best CV; handles small continuous features', sTDL)],
        [P('Heart', sTD), P('Naive Bayes', sTD),
         P('Strong on correlated cardiac markers', sTDL)],
        [P("Parkinson's", sTD), P('RF depth=10', sTD),
         P('Ensemble; max_depth=10 prevents overfitting', sTDL)],
        [P('Breast Cancer', sTD), P('Logistic Reg.', sTD),
         P('Linear separability in FNA feature space', sTDL)],
        [P('Kidney CT', sTD), P('VGG-16 TL', sTD),
         P('ImageNet weights; fine-tuned last layers', sTDL)],
    ]
    algo_cw = [COL3*0.18, COL3*0.22, COL3*0.60]
    algo_t = card_table(algo_grid, algo_cw)

    arch_rows += [[algo_t], [SP(8)],
        [P('▼', sBodyC)], [SP(4)],
        [P('OUTPUT LAYER', S('a4', TB, 22, 28, TA_CENTER, YELLOW))],
        [SP(6)],
    ]

    out_data = [
        [P('Patient Portal', S('op', TB, 20, 26, TA_CENTER, PRIMARY)),
         P('Doctor Portal', S('od', TB, 20, 26, TA_CENTER, GREEN))],
        [P('Binary Prediction\n+ Gemini Explanation', sBodyC),
         P('Confidence %  ·  Feature Importance\nReference Ranges  ·  Clinical Summary', sBodyC)],
    ]
    out_cw = [COL3/2 - 4, COL3/2 - 4]
    out_t = Table(out_data, colWidths=out_cw, hAlign='CENTER')
    out_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#dce8f5')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#ddf0e8')),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    arch_rows += [[out_t]]

    arch_t = Table(arch_rows, colWidths=[COL3])
    arch_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
    ]))

    # ── Algorithm Detail ───────────────────────────────────────────────────────
    eval_rows = [
        [P('Algorithms & Evaluation', sSectHead)],
        [SP(6)],
        [P('8 Classifiers Evaluated Per Disease', sSubHead)],
        [P('Naïve Bayes · Logistic Regression · k-NN · SVM (RBF) · '
           'Decision Tree · Random Forest · XGBoost · Extra Trees', sBody)],
        [SP(6)],
        [P('5-Fold Stratified Cross-Validation', sSubHead)],
        [P('StratifiedKFold(n=5, shuffle=True, random_state=42)\n'
           'Reports: mean accuracy ± std, confusion matrix, ROC/AUC', sBody)],
        [SP(8)],
    ]

    perf_data = [
        [P('Disease', sTH), P('Best Model', sTH), P('Test Acc', sTH),
         P('CV Mean', sTH), P('±Std', sTH), P('AUC', sTH)],
        [P('Breast Cancer', sTD), P('Logistic Reg.', sTD),
         P('98.2%', S('g3',TB,19,24,TA_CENTER,GREEN)), P('97.4%', sTD), P('1.7', sTD),
         P('0.99', S('g4',TB,19,24,TA_CENTER,GREEN))],
        [P("Parkinson's",   sTD), P('RF depth=10',   sTD),
         P('92.3%', S('g',TB,19,24,TA_CENTER,GREEN)), P('88.2%', sTD), P('4.8', sTD),
         P('0.97', S('g2',TB,19,24,TA_CENTER,GREEN))],
        [P('Kidney CT',     sTD), P('VGG-16 TL',     sTD),
         P('99.0%', S('g5',TB,19,24,TA_CENTER,GREEN)), P('—', sTD), P('—', sTD),
         P('—', sTD)],
        [P('Heart Disease', sTD), P('Naive Bayes',   sTD),
         P('85.2%', sTD), P('84.1%', sTD), P('4.3', sTD), P('0.92', sTD)],
        [P('Diabetes',      sTD), P('GaussianNB',    sTD),
         P('74.7%', sTD), P('76.0%', sTD), P('1.7', sTD), P('0.84', sTD)],
    ]
    pcw = [COL3*0.20, COL3*0.21, COL3*0.13, COL3*0.13, COL3*0.10, COL3*0.10]
    # adjust to sum to COL3
    pcw[-1] = COL3 - sum(pcw[:-1])
    perf_t = card_table(perf_data, pcw)

    eval_rows += [[perf_t], [SP(10)],
        [P('Overfitting Prevention', sSubHead)],
        [P('Random Forest and Decision Tree constrained to <b>max_depth=10</b> — '
           'prevents memorisation while maintaining competitive test accuracy '
           'and stable cross-validation scores.', sBody)],
        [SP(6)],
        [P('CNN Architecture — Kidney CT', sSubHead)],
        [P('VGG-16 pretrained on ImageNet. Final dense layers replaced: '
           'GlobalAvgPool → Dense(256, ReLU) → Dropout(0.5) → Dense(4, Softmax). '
           'Classes: Normal · Cyst · Stone · Tumor. '
           'Dataset: 12,446 CT images, 80/10/10 split.', sBody)],
    ]

    eval_t = Table(eval_rows, colWidths=[COL3])
    eval_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
    ]))

    row1 = Table([[mot_t, arch_t, eval_t]],
                 colWidths=[COL3, COL3, COL3],
                 hAlign='LEFT')
    row1.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('COLPADDING',   (0,0), (-1,-1), 0),
        ('ALIGN',        (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    # Add gap between columns via spacer column
    row1 = Table([[mot_t, Spacer(COL_GAP,1), arch_t, Spacer(COL_GAP,1), eval_t]],
                 colWidths=[COL3, COL_GAP, COL3, COL_GAP, COL3])
    row1.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    story += [row1, SP(20)]

    # ════════════════════════ ROW 2: Results Plots ════════════════════════════
    plot_w = (BODY_W - 2*COL_GAP) / 3

    plot_w = (BODY_W - COL_GAP) / 2

    roc   = rimg('roc_curves.png',  plot_w)
    cvbox = rimg('cv_all_models.png', plot_w)

    def plot_cell(items, caption):
        cell = items + [P(caption, sCaption)]
        t = Table([[i] for i in cell], colWidths=[plot_w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, BORDER),
        ]))
        return t

    roc_cell = plot_cell(roc,   'Fig. A. ROC Curves — AUC per disease')
    cv_cell  = plot_cell(cvbox, 'Fig. B. 5-Fold CV Accuracy — All Models × All Diseases')

    plots_row = Table([[roc_cell, Spacer(COL_GAP,1), cv_cell]],
                      colWidths=[plot_w, COL_GAP, plot_w])
    plots_row.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    story += [plots_row, SP(20)]

    # ════════════════════ ROW 3: Screenshots + Conclusion ════════════════════
    # 4 screenshots: landing | detected | not detected | doctor portal
    scr_w = (BODY_W*0.65 - COL_GAP*3) / 4

    def scr_cell(fname, cap):
        items = simg(fname, scr_w)
        if not items: return Table([[P('', sBody)]], colWidths=[scr_w])
        items.append(P(cap, sCaption))
        t = Table([[i] for i in items], colWidths=[scr_w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, BORDER),
        ]))
        return t

    s1 = scr_cell('p01_landing.png',              'Landing — chatbot + modules')
    s2 = scr_cell('p08_heart_detected.png',        'Heart Disease Detected — patient view')
    s3 = scr_cell('p09_heart_not_detected.png',    'No Heart Disease Detected — patient view')
    s4 = scr_cell('d06_doctor_heart_detected.png', 'Doctor Portal — Heart Disease Detected')

    scr_row = Table([[s1, Spacer(COL_GAP,1), s2, Spacer(COL_GAP,1), s3, Spacer(COL_GAP,1), s4]],
                    colWidths=[scr_w, COL_GAP, scr_w, COL_GAP, scr_w, COL_GAP, scr_w])
    scr_row.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))

    # Conclusion column
    concl_w = BODY_W * 0.35 - COL_GAP
    concl_rows = [
        [P('Conclusion', sSectHead)],
        [SP(8)],
        [P('<b>What we built:</b>', sSubHead)],
        [P('A production-ready Flask platform serving 5 disease-screening modules '
           'through dual clinical portals, with full evaluation pipeline.', sBody)],
        [SP(8)],
        [P('<b>Key results:</b>', sSubHead)],
        [P('✦  Breast Cancer: 98.2% acc, AUC 0.99', sBullet)],
        [P('✦  Kidney CT (VGG-16): 99.0% accuracy', sBullet)],
        [P("✦  Parkinson's RF: 92.3% acc, 88.2% CV", sBullet)],
        [P('✦  Heart Disease NB: 85.2% acc, AUC 0.92', sBullet)],
        [SP(8)],
        [P('<b>Novel contributions:</b>', sSubHead)],
        [P('✦  Unified multi-disease platform (5 modules, 2 portals)', sBullet)],
        [P('✦  LLM-augmented clinical summaries via Gemini 2.5', sBullet)],
        [P('✦  Depth-constrained ensemble with CV validation', sBullet)],
        [P('✦  Doctor Portal with feature attribution + PDF export', sBullet)],
        [SP(8)],
        [P('<b>Future work:</b>', sSubHead)],
        [P('✦  Grad-CAM visualisations for CNN explainability', sBullet)],
        [P('✦  SMOTE for class-imbalanced datasets', sBullet)],
        [P('✦  Cloud deployment with ONNX runtime', sBullet)],
        [SP(10)],
        [HR(color=PRIMARY)],
        [SP(6)],
        [P('github.com/honeyreddydaram/NeuralMed', S('gh', TB, 20, 26, TA_CENTER, PRIMARY))],
        [P('University of Florida · EED Symposium 2026', S('uf', T, 18, 24, TA_CENTER, MUTED))],
    ]
    concl_t = Table(concl_rows, colWidths=[concl_w])
    concl_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD),
        ('LEFTPADDING', (0,0), (-1,-1), 18),
        ('RIGHTPADDING', (0,0), (-1,-1), 18),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
    ]))

    bottom_row = Table(
        [[scr_row, Spacer(COL_GAP,1), concl_t]],
        colWidths=[BODY_W*0.65, COL_GAP, concl_w]
    )
    bottom_row.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    story += [bottom_row]

    return story

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    out = '/Users/honey/Downloads/Deep-Learning-Project/NeuralMed_Poster.pdf'

    doc = BaseDocTemplate(
        out, pagesize=(PW, PH),
        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
        title='NeuralMed Poster', author='Honey Reddy Daram',
    )
    frame = Frame(M, M, BODY_W, PH - 2*M, id='main', showBoundary=0)
    template = PageTemplate(id='poster', frames=[frame], onPage=draw_bg)
    doc.addPageTemplates([template])
    doc.build(build())
    print(f'Poster → {out}')
