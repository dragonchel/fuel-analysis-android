# regression_core_android.py
import os
import json
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

MODEL_FILE = "trained_model.json"
CO2_PER_LITER = 2.68          
COST_PER_TON_CO2 = 50         

# Базовые коэффициенты по умолчанию (если датасет еще не загружался)
DEFAULT_MODEL = {
    "intercept": 10.50,
    "coef_weight": 0.78,
    "coef_speed": -0.12,
    "margin_of_error": 2.35,
    "r2": 0.54,
    "is_trained": False
}

def load_model():
    if os.path.exists(MODEL_FILE):
        try:
            with open(MODEL_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_MODEL.copy()
    return DEFAULT_MODEL.copy()

def save_model(model_data):
    with open(MODEL_FILE, "w") as f:
        json.dump(model_data, f)

def train_model_from_excel(file_path):
    """ Математический эквивалент run_regression из Windows на чистом NumPy """
    try:
        df = pd.read_excel(file_path, sheet_name="Данные")
        X = df[['Вес, т', 'Скорость, км/ч']].values
        Y = df['Расходтоплива, л/100 км'].values
        
        # Метод наименьших квадратов (МНК): (X^T * X)^-1 * X^T * Y
        X_design = np.hstack([np.ones((X.shape[0], 1)), X])
        beta = np.linalg.inv(X_design.T @ X_design) @ X_design.T @ Y
        
        intercept, coef_weight, coef_speed = beta[0], beta[1], beta[2]
        
        Y_pred = X_design @ beta
        residuals = Y - Y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((Y - np.mean(Y))**2)
        r2 = 1 - (ss_res / ss_tot)
        
        # Оценка погрешности (Аналог распределения Стьюдента)
        dof = X.shape[0] - 3
        se = np.sqrt(ss_res / dof) if dof > 0 else 0.1
        t_crit = 1.96 if dof > 30 else 2.0 + (2.5 / max(dof, 1))
        margin_of_error = se * t_crit
        
        model_data = {
            "intercept": float(intercept),
            "coef_weight": float(coef_weight),
            "coef_speed": float(coef_speed),
            "margin_of_error": float(margin_of_error),
            "r2": float(r2),
            "is_trained": True
        }
        save_model(model_data)
        return {"success": True, "data": model_data, "total_rows": len(df)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_single_trip(w, s, actual_f):
    model = load_model()
    predicted_fuel = model["intercept"] + (model["coef_weight"] * w) + (model["coef_speed"] * s)
    upper_bound = predicted_fuel + model["margin_of_error"]
    extra_fuel = max(actual_f - upper_bound, 0.0)
    damage = (extra_fuel * CO2_PER_LITER / 1000) * COST_PER_TON_CO2
    
    return {
        "predicted": predicted_fuel,
        "upper_bound": upper_bound,
        "extra_fuel": extra_fuel,
        "damage": damage,
        "is_violation": extra_fuel > 0
    }

def export_to_pdf_android(output_path, report_text):
    """ Создание чистого PDF-отчета """
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1565C0"))
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=11, leading=16)
        
        story.append(Paragraph("<b>ОТЧЕТ СИСТЕМЫ МОНИТОРИНГА ТОПЛИВА</b>", title_style))
        story.append(Spacer(1, 15))
        
        for line in report_text.split('\n'):
            if line.strip():
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 5))
                
        doc.build(story)
        return True
    except Exception as e:
        return False