# regression_core_android.py
import os
import json
import csv
import math
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

MODEL_FILE = "trained_model.json"
CO2_PER_LITER = 2.68          
COST_PER_TON_CO2 = 50         

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

def determinant3x3(m):
    """ Вычисление определителя матрицы 3x3 (Правило треугольника) """
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

def train_model_from_csv(file_path):
    """ Математический эквивалент МНК регрессии на чистом Python и CSV """
    try:
        weights = []
        speeds = []
        fuels = []
        
        # Чтение данных из CSV файла
        with open(file_path, mode='r', encoding='utf-8') as f:
            # Автоопределение разделителя (запятая или точка с запятой)
            sample = f.read(2048)
            f.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                # Очищаем ключи от пробелов на случай неточных заголовков
                clean_row = {k.strip(): v for k, v in row.items() if k}
                
                # Преобразуем строки в числа (обрабатывая возможные запятые вместо точек)
                w = float(str(clean_row['Вес, т']).replace(',', '.'))
                s = float(str(clean_row['Скорость, км/ч']).replace(',', '.'))
                f_val = float(str(clean_row['Расходтоплива, л/100 км']).replace(',', '.'))
                
                weights.append(w)
                speeds.append(s)
                fuels.append(f_val)
                
        n = len(fuels)
        if n < 4:
            return {"success": False, "error": "Недостаточно данных для обучения (требуется минимум 4 строки)"}
            
        # Нахождение необходимых сумм для построения нормальных уравнений МНК
        sum_w = sum(weights)
        sum_s = sum(speeds)
        sum_f = sum(fuels)
        
        sum_w2 = sum(w**2 for w in weights)
        sum_s2 = sum(s**2 for s in speeds)
        sum_ws = sum(w * s for w, s in zip(weights, speeds))
        
        sum_wf = sum(w * f for w, f in zip(weights, fuels))
        sum_sf = sum(s * f for s, f in zip(speeds, fuels))
        
        # Матрица системы X^T * X
        M = [
            [float(n), sum_w, sum_s],
            [sum_w, sum_w2, sum_ws],
            [sum_s, sum_ws, sum_s2]
        ]
        
        det_M = determinant3x3(M)
        if abs(det_M) < 1e-7:
            return {"success": False, "error": "Матрица данных вырождена (факторы линейно зависимы)"}
            
        # Матрицы для нахождения неизвестных методом Крамера
        M0 = [[sum_f, sum_w, sum_s], [sum_wf, sum_w2, sum_ws], [sum_sf, sum_ws, sum_s2]]
        M1 = [[float(n), sum_f, sum_s], [sum_w, sum_wf, sum_ws], [sum_s, sum_sf, sum_s2]]
        M2 = [[float(n), sum_w, sum_f], [sum_w, sum_w2, sum_wf], [sum_s, sum_ws, sum_sf]]
        
        intercept = determinant3x3(M0) / det_M
        coef_weight = determinant3x3(M1) / det_M
        coef_speed = determinant3x3(M2) / det_M
        
        # Расчет коэффициента детерминации R^2
        mean_f = sum_f / n
        ss_tot = sum((f - mean_f)**2 for f in fuels)
        
        ss_res = 0.0
        for w, s, f_val in zip(weights, speeds, fuels):
            pred = intercept + (coef_weight * w) + (coef_speed * s)
            ss_res += (f_val - pred)**2
            
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Расчет статистической погрешности (Критерий Стьюдента)
        dof = n - 3
        se = math.sqrt(ss_res / dof) if dof > 0 else 0.1
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
        return {"success": True, "data": model_data, "total_rows": n}
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