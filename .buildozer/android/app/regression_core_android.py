# regression_core_android.py

# ЭКОЛОГИЧЕСКИЕ КОНСТАНТЫ
CO2_PER_LITER = 2.68
COST_PER_TON_CO2 = 50

# ВАШИ КОЭФФИЦИЕНТЫ (из модели Windows)
INTERCEPT = 10.50
COEF_WEIGHT = 0.78
COEF_SPEED = -0.12
MARGIN_OF_ERROR = 2.35
R2_VALUE = 0.54

def calculate_single_trip(w, s, actual_f):
    """
    Расчет перерасхода по линейной формуле.
    w: вес, s: скорость, actual_f: фактический расход.
    """
    predicted_fuel = INTERCEPT + (COEF_WEIGHT * w) + (COEF_SPEED * s)
    upper_bound = predicted_fuel + MARGIN_OF_ERROR
    extra_fuel = max(actual_f - upper_bound, 0.0)
    
    # Расчет ущерба
    damage = (extra_fuel * CO2_PER_LITER / 1000) * COST_PER_TON_CO2
    
    return {
        "predicted": predicted_fuel,
        "upper_bound": upper_bound,
        "extra_fuel": extra_fuel,
        "damage": damage,
        "is_violation": extra_fuel > 0
    }