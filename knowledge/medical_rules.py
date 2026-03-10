
import json
import os

# ================== ЗАГРУЗКА ДАННЫХ ==================
BASE_PATH = os.path.dirname(__file__)


def load_knowledge(filename):
    with open(os.path.join(BASE_PATH, filename), "r", encoding="utf-8") as f:
        return json.load(f)


BMI_DATA = load_knowledge("bmi.json")
BP_DATA = load_knowledge("blood_pressure.json")
PULSE_DATA = load_knowledge("pulse.json")
SLEEP_DATA = load_knowledge("sleep.json")
ACTIVITY_DATA = load_knowledge("physical_activity.json")
AGE_DATA = load_knowledge("age_risk.json")
DISCLAIMERS = load_knowledge("disclaimers.json")


# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================
def calculate_bmi(weight, height):
    return round(weight / (height / 100) ** 2, 1)


def find_category(value, categories):
    for c in categories:
        if c.get("min") <= value <= c.get("max"):
            return c
    return categories[0] if value < categories[0]["min"] else categories[-1]


def find_bp_category(sys, dia):
    for c in BP_DATA["categories"]:
        if (
            c["sys_min"] <= sys <= c["sys_max"]
            and c["dia_min"] <= dia <= c["dia_max"]
        ):
            return c

    # fallback — ближайшая категория
    return min(
        BP_DATA["categories"],
        key=lambda c: abs(sys - (c["sys_min"] + c["sys_max"]) / 2)
        + abs(dia - (c["dia_min"] + c["dia_max"]) / 2),
    )


def filter_recommendations(recommendations, sex):
    result = []
    for r in recommendations:
        if isinstance(r, str):
            result.append(r)
        elif isinstance(r, dict) and r.get("sex") == sex:
            result.append(r["text"])
    return result


# ================== СБОР ВСЕХ ПОКАЗАТЕЛЕЙ ==================
def collect_health_data(user):
    sex = user.get("sex")
    data = []

    # BMI
    bmi = calculate_bmi(user["weight"], user["height"])
    bmi_cat = find_category(bmi, BMI_DATA["categories"])
    data.append({
        "key": "bmi",
        "title": "Индекс массы тела (BMI)",
        "value": f"{bmi}",
        "label": bmi_cat["label"],
        "risk": bmi_cat["risk"],
        "recommendations": filter_recommendations(bmi_cat["recommendations"], sex)
    })

    # Blood pressure
    sys, dia = user["pressure"]
    bp_cat = find_bp_category(sys, dia)
    data.append({
        "key": "pressure",
        "title": "Артериальное давление",
        "value": f"{sys}/{dia} мм рт. ст.",
        "label": bp_cat["label"],
        "risk": bp_cat["risk"],
        "recommendations": filter_recommendations(bp_cat["recommendations"], sex)
    })

    # Pulse
    pulse_cat = find_category(user["pulse"], PULSE_DATA["categories"])
    data.append({
        "key": "pulse",
        "title": "Пульс в покое",
        "value": f"{user['pulse']} уд/мин",
        "label": pulse_cat["label"],
        "risk": pulse_cat["risk"],
        "recommendations": filter_recommendations(pulse_cat["recommendations"], sex)
    })

    # Sleep
    sleep_cat = find_category(user["sleep"], SLEEP_DATA["categories"])
    data.append({
        "key": "sleep",
        "title": "Сон",
        "value": f"{user['sleep']} ч/сут",
        "label": sleep_cat["label"],
        "risk": sleep_cat["risk"],
        "recommendations": filter_recommendations(sleep_cat["recommendations"], sex)
    })

    # Activity
    activity_map = {"низкий": 0, "средний": 3, "высокий": 6}
    activity_value = activity_map.get(user["activity"], 0)
    activity_cat = find_category(activity_value, ACTIVITY_DATA["categories"])
    data.append({
        "key": "activity",
        "title": "Физическая активность",
        "value": user["activity"],
        "label": activity_cat["label"],
        "risk": activity_cat["risk"],
        "recommendations": filter_recommendations(activity_cat["recommendations"], sex)
    })

    # Age
    age_cat = find_category(user["age"], AGE_DATA["categories"])
    data.append({
        "key": "age",
        "title": "Возраст",
        "value": f"{user['age']} лет",
        "label": age_cat["label"],
        "risk": age_cat["risk"],
        "recommendations": filter_recommendations(age_cat["recommendations"], sex)
    })

    return data


# ================== 📊 СТАТУС ==================
def generate_status(user):
    lines = ["📊 Текущий статус здоровья:"]
    for item in collect_health_data(user):
        lines.append(
            f"• {item['title']}: {item['value']} ({item['label']})"
        )
    lines.append(f"\nℹ️ {DISCLAIMERS.get('medical_disclaimer', '')}")
    return "\n".join(lines)


# ================== ⚠️ РИСКИ ==================
def generate_risks(user):
    lines = ["⚠️ Выявленные риски:"]
    for item in collect_health_data(user):
        if item["risk"]:
            lines.append(
                f"\n🔹 {item['title']}\n{item['risk']}"
            )
    lines.append(f"\nℹ️ {DISCLAIMERS.get('medical_disclaimer', '')}")
    return "\n".join(lines)


# ================== 🧠 РЕКОМЕНДАЦИИ ==================
def generate_recommendations(user):
    lines = ["🧠 Персональные рекомендации:"]
    for item in collect_health_data(user):
        if item["recommendations"]:
            lines.append(f"\n🔹 {item['title']}")
            for r in item["recommendations"]:
                lines.append(f"• {r}")

    lines.append(f"\nℹ️ {DISCLAIMERS.get('medical_disclaimer', '')}")
    return "\n".join(lines)
