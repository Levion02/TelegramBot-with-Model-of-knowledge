def health_risk_score(features):
    """
    features = {
        'bmi': float,
        'pulse_dev': int,
        'sys': int,
        'dia': int,
        'sleep_def': float,
        'activity': int,
        'age': int
    }
    """

    score = 0

    # Весовые коэффициенты (экспертная инициализация)
    score += (features['bmi'] - 21) * 2
    score += features['pulse_dev'] * 0.8
    score += max(0, features['sys'] - 120) * 0.7
    score += max(0, features['dia'] - 80) * 0.6
    score += features['sleep_def'] * 3
    score += features['activity'] * 5
    score += max(0, features['age'] - 30) * 0.5

    return max(0, min(100, round(score)))