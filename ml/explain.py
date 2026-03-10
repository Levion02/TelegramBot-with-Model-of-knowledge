def explain_risk(features):
    explanations = []

    if features['bmi'] > 25:
        explanations.append("⚠️ Повышенный индекс массы тела увеличивает метаболическую нагрузку.")
    elif features['bmi'] < 18.5:
        explanations.append("⚠️ Недостаточная масса тела может указывать на дефицит ресурсов организма.")

    if features['sys'] > 130 or features['dia'] > 85:
        explanations.append("⚠️ Повышенное артериальное давление увеличивает риск сердечно-сосудистых заболеваний.")

    if features['pulse_dev'] > 15:
        explanations.append("⚠️ Отклонение пульса от нормы может указывать на перенапряжение сердечно-сосудистой системы.")

    if features['sleep_def'] > 1:
        explanations.append("⚠️ Недостаток сна негативно влияет на иммунную и нервную систему.")

    if features['activity'] > 0:
        explanations.append("ℹ️ Низкий уровень физической активности снижает защитные механизмы организма.")

    if not explanations:
        explanations.append("✅ Значимых факторов риска не выявлено.")

    return explanations