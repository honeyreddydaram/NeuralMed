"""Capture all NeuralMed screens: patient portal (forms + positive/negative results)
and doctor portal (forms + results with confidence/importance)."""
import time, os
from playwright.sync_api import sync_playwright

BASE   = 'http://localhost:5001'
OUTDIR = '/Users/honey/Downloads/Deep-Learning-Project/docs_new'
os.makedirs(OUTDIR, exist_ok=True)

def shot(page, name, scroll_to=None, scroll_bottom=False):
    if scroll_to:
        page.evaluate(f"var el=document.getElementById('{scroll_to}'); if(el) el.scrollIntoView({{behavior:'instant',block:'start'}}); else window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.6)
    elif scroll_bottom:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.6)
    path = os.path.join(OUTDIR, name)
    page.screenshot(path=path, full_page=False)
    print(f'  ✓ {name}')

def go(page, path, wait='networkidle'):
    page.goto(f'{BASE}{path}', wait_until=wait, timeout=15000)
    time.sleep(0.6)

def post(page, path, data: dict):
    page.goto(f'{BASE}{path}', wait_until='networkidle', timeout=15000)
    for name, value in data.items():
        selector = f'[name="{name}"]'
        el = page.query_selector(selector)
        if el:
            tag = el.evaluate('el => el.tagName.toLowerCase()')
            typ = el.get_attribute('type') or ''
            if tag == 'select':
                el.select_option(str(value))
            elif typ == 'radio':
                page.check(f'[name="{name}"][value="{value}"]')
            else:
                el.fill(str(value))
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(1.0)

# ── Sample data ────────────────────────────────────────────────────────────────
DIABETES_POS = dict(pregnancies=6, Glucose=148, BloodPressure=72,
                    skin_thickness=35, insulin=0, BMI=33.6,
                    DiabetesPedigreeFunction=0.627, Age=50)
DIABETES_NEG = dict(pregnancies=1, Glucose=85, BloodPressure=66,
                    skin_thickness=29, insulin=0, BMI=26.6,
                    DiabetesPedigreeFunction=0.351, Age=31)

HEART_POS = dict(age=67, sex=1, cp=0, trestbps=160, chol=286, fbs=0,
                 restecg=2, thalach=108, exang=1, oldpeak=1.5,
                 slope=1, ca=3, thal=2)
HEART_NEG = dict(age=41, sex=1, cp=1, trestbps=130, chol=204, fbs=0,
                 restecg=2, thalach=172, exang=0, oldpeak=1.4,
                 slope=0, ca=0, thal=2)

LIVER_POS = dict(age=65, gender=1, total_bilirubin=4.1, direct_bilirubin=1.8,
                 alkaline_phosphotase=490, alamine_aminotransferase=180,
                 aspartate_aminotransferase=210, total_proteins=5.8,
                 albumin=2.4, albumin_globulin_ratio=0.7)
LIVER_NEG = dict(age=35, gender=0, total_bilirubin=0.5, direct_bilirubin=0.1,
                 alkaline_phosphotase=100, alamine_aminotransferase=18,
                 aspartate_aminotransferase=22, total_proteins=7.2,
                 albumin=4.0, albumin_globulin_ratio=1.2)

PARK_POS = dict(MDVPFO=119.992, MDVPFHI=157.302, MDVPFLO=74.997,
                MDVPJ=0.00784, RPDE=0.458359, DFA=0.819521,
                spread2=0.266482, D2=2.301442)
PARK_NEG = dict(MDVPFO=197.076, MDVPFHI=206.896, MDVPFLO=192.055,
                MDVPJ=0.00289, RPDE=0.284654, DFA=0.634068,
                spread2=0.134272, D2=1.794820)

BCANCER_MAL = dict(
    texture_mean=21.6, smoothness_mean=0.103, compactness_mean=0.145,
    concave_points_mean=0.088, symmetry_mean=0.193, fractal_dimension_mean=0.062,
    texture_se=2.5, area_se=100, smoothness_se=0.006, compactness_se=0.03,
    concavity_se=0.04, concave_points_se=0.013, symmetry_se=0.02, fractal_dimension_se=0.004,
    texture_worst=29.3, area_worst=1422, smoothness_worst=0.15, compactness_worst=0.35,
    concavity_worst=0.40, concave_points_worst=0.18, symmetry_worst=0.30,
    fractal_dimension_worst=0.09)
BCANCER_BEN = dict(
    texture_mean=17.9, smoothness_mean=0.083, compactness_mean=0.080,
    concave_points_mean=0.026, symmetry_mean=0.174, fractal_dimension_mean=0.058,
    texture_se=1.5, area_se=40, smoothness_se=0.004, compactness_se=0.02,
    concavity_se=0.02, concave_points_se=0.007, symmetry_se=0.015, fractal_dimension_se=0.003,
    texture_worst=25.4, area_worst=558, smoothness_worst=0.11, compactness_worst=0.15,
    concavity_worst=0.12, concave_points_worst=0.07, symmetry_worst=0.22,
    fractal_dimension_worst=0.07)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = ctx.new_page()

    print('\n── Static Pages ─────────────────────────────────────')
    go(page, '/')
    shot(page, 'p01_landing.png')

    go(page, '/services')
    shot(page, 'p02_services.png')

    go(page, '/precautions')
    shot(page, 'p03_precautions.png')

    print('\n── Patient Portal — Diabetes ────────────────────────')
    go(page, '/diabetes')
    shot(page, 'p04_diabetes_form.png')

    post(page, '/diabetes', DIABETES_POS)
    shot(page, 'p05_diabetes_detected.png', scroll_bottom=True)

    post(page, '/diabetes', DIABETES_NEG)
    shot(page, 'p06_diabetes_not_detected.png', scroll_bottom=True)

    print('\n── Patient Portal — Heart ───────────────────────────')
    go(page, '/heart')
    shot(page, 'p07_heart_form.png')

    post(page, '/heart', HEART_POS)
    shot(page, 'p08_heart_detected.png', scroll_bottom=True)

    post(page, '/heart', HEART_NEG)
    shot(page, 'p09_heart_not_detected.png', scroll_bottom=True)

    print('\n── Patient Portal — Liver ───────────────────────────')
    go(page, '/liver')
    shot(page, 'p10_liver_form.png')

    post(page, '/liver', LIVER_POS)
    shot(page, 'p11_liver_positive.png', scroll_to='resultSection')

    post(page, '/liver', LIVER_NEG)
    shot(page, 'p12_liver_negative.png', scroll_to='resultSection')

    print('\n── Patient Portal — Parkinsons ──────────────────────')
    go(page, '/parkinsons')
    shot(page, 'p13_parkinsons_form.png')

    post(page, '/parkinsons', PARK_POS)
    shot(page, 'p14_parkinsons_detected.png', scroll_bottom=True)

    post(page, '/parkinsons', PARK_NEG)
    shot(page, 'p15_parkinsons_not_detected.png', scroll_bottom=True)

    print('\n── Patient Portal — Breast Cancer ───────────────────')
    go(page, '/bcancer')
    shot(page, 'p16_bcancer_form.png')

    post(page, '/bcancer', BCANCER_MAL)
    shot(page, 'p17_bcancer_malignant.png', scroll_bottom=True)

    post(page, '/bcancer', BCANCER_BEN)
    shot(page, 'p18_bcancer_benign.png', scroll_bottom=True)

    print('\n── Patient Portal — Kidney ──────────────────────────')
    go(page, '/kidney')
    shot(page, 'p19_kidney_form.png')

    print('\n── Doctor Portal ────────────────────────────────────')
    go(page, '/doctor')
    shot(page, 'd01_doctor_portal.png')

    go(page, '/doctor/diabetes')
    shot(page, 'd02_doctor_diabetes_form.png')

    post(page, '/doctor/diabetes', DIABETES_POS)
    shot(page, 'd03_doctor_diabetes_detected.png', scroll_to='resultSection')

    post(page, '/doctor/diabetes', DIABETES_NEG)
    shot(page, 'd04_doctor_diabetes_not_detected.png', scroll_to='resultSection')

    go(page, '/doctor/heart')
    shot(page, 'd05_doctor_heart_form.png')

    post(page, '/doctor/heart', HEART_POS)
    shot(page, 'd06_doctor_heart_detected.png', scroll_to='resultSection')

    post(page, '/doctor/heart', HEART_NEG)
    shot(page, 'd07_doctor_heart_not_detected.png', scroll_to='resultSection')

    go(page, '/doctor/liver')
    shot(page, 'd08_doctor_liver_form.png')

    post(page, '/doctor/liver', LIVER_POS)
    shot(page, 'd09_doctor_liver_positive.png', scroll_to='resultSection')

    post(page, '/doctor/liver', LIVER_NEG)
    shot(page, 'd10_doctor_liver_negative.png', scroll_to='resultSection')

    go(page, '/doctor/parkinsons')
    shot(page, 'd11_doctor_parkinsons_form.png')

    post(page, '/doctor/parkinsons', PARK_POS)
    shot(page, 'd12_doctor_parkinsons_detected.png', scroll_to='resultSection')

    post(page, '/doctor/parkinsons', PARK_NEG)
    shot(page, 'd13_doctor_parkinsons_not_detected.png', scroll_to='resultSection')

    go(page, '/doctor/bcancer')
    shot(page, 'd14_doctor_bcancer_form.png')

    post(page, '/doctor/bcancer', BCANCER_MAL)
    shot(page, 'd15_doctor_bcancer_malignant.png', scroll_to='resultSection')

    post(page, '/doctor/bcancer', BCANCER_BEN)
    shot(page, 'd16_doctor_bcancer_benign.png', scroll_to='resultSection')

    browser.close()
    print('\nAll screenshots done.')
