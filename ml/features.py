

def calculate_bmi(weight, height):
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)


def bmi_category(bmi):
    if bmi < 18.5:
        return "дефицит массы тела"
    elif bmi < 25:
        return "норма"
    elif bmi < 30:
        return "избыточная масса тела"
    else:
        return "ожирение"


def pulse_deviation(pulse):
    return abs(pulse - 70)


def sleep_deficit(hours):
    return max(0, 8 - hours)


def activity_score(level):
    return {
        "низкий": 2,
        "средний": 1,
        "высокий": 0
    }.get(level, 1)