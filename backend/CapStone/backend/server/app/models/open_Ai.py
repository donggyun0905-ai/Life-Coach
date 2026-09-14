# server/app/models/open_Ai.py
#
# 건강데이터 예측/피드백을 순수 통계 + 규칙 기반 템플릿으로 생성한다.
# (Gemini API를 쓰지 않음 — 무료/무제한, 외부 키 유출·만료 위험 없음)
# 알약 사진 분석(pill_ai.py)은 이미지 인식이 꼭 필요해서 그대로 Gemini Vision을 씁니다.

GOALS = {
    "steps": 4000,
    "distance_m": 3000,
    "calories_kcal": 2000,
    "sleep_minutes": 480,
}


def _avg(rows, key):
    values = [r[key] for r in rows if r.get(key) is not None]
    return sum(values) / len(values) if values else 0.0


def _round1(value):
    return round(value, 1) if value is not None else None


def _health_score(avgs):
    ratios = []
    for key, goal in GOALS.items():
        ratios.append(min(avgs[key] / goal, 1.0) if goal else 1.0)
    return round(sum(ratios) / len(ratios) * 100)


def _weakest_metric(avgs):
    ratios = {key: (avgs[key] / goal if goal else 1.0) for key, goal in GOALS.items()}
    return min(ratios, key=ratios.get)


ADVICE_TEMPLATES = {
    "steps": "요즘 걸음 수가 목표보다 적어요. 하루 10분이라도 가볍게 걸어보는 건 어떨까요?",
    "distance_m": "이동 거리가 조금 부족해요. 가까운 거리는 걸어서 다녀보세요.",
    "calories_kcal": "활동량이 다소 낮아요. 집안일이나 가벼운 스트레칭도 도움이 됩니다.",
    "sleep_minutes": "수면 시간이 부족해요. 잠자리에 조금 더 일찍 들어보시는 걸 권해드려요.",
    "good": "지금처럼 꾸준히 잘 관리하고 계세요! 이 페이스를 유지해보세요.",
}


def _one_line_advice(avgs, score):
    if score >= 85:
        return ADVICE_TEMPLATES["good"]
    return ADVICE_TEMPLATES[_weakest_metric(avgs)]


def _summary_of_last_month(avgs30):
    return (
        f"지난 한 달간 하루 평균 {round(avgs30['steps'])}보 걸으셨고, "
        f"평균 수면 시간은 {round(avgs30['sleep_minutes'])}분, "
        f"평균 칼로리 소모는 {_round1(avgs30['calories_kcal'])}kcal였어요."
    )


def _josa_i_ga(word):
    """마지막 글자 받침 유무로 '이/가' 조사를 고른다."""
    last = word[-1]
    if "가" <= last <= "힣":
        return "이" if (ord(last) - ord("가")) % 28 != 0 else "가"
    return "가"


def _habit_recommendation(health30):
    # 최근 15일 vs 그 이전 15일 비교로 추세 파악
    if len(health30) < 10:
        return "데이터가 더 쌓이면 습관 변화를 분석해드릴게요."

    mid = len(health30) // 2
    earlier, recent = health30[:mid], health30[mid:]

    diffs = {}
    for key in GOALS:
        earlier_avg = _avg(earlier, key)
        recent_avg = _avg(recent, key)
        diffs[key] = recent_avg - earlier_avg

    trend_key = max(diffs, key=lambda k: abs(diffs[k]))
    trend_value = diffs[trend_key]

    labels = {
        "steps": "걸음 수",
        "distance_m": "이동 거리",
        "calories_kcal": "활동 칼로리",
        "sleep_minutes": "수면 시간",
    }

    if abs(trend_value) < 1:
        return "최근 습관이 꾸준히 안정적으로 유지되고 있어요."

    label = labels[trend_key]
    josa = _josa_i_ga(label)
    if trend_value > 0:
        return f"최근 {label}{josa} 이전보다 늘고 있어요. 좋은 흐름이니 계속 유지해보세요!"
    return f"최근 {label}{josa} 이전보다 줄었어요. 다시 조금씩 늘려보는 걸 권해드려요."


def run_open_ai_full_report(health15, health30):
    avgs15 = {key: _avg(health15, key) for key in GOALS}
    avgs30 = {key: _avg(health30, key) for key in GOALS}
    avg_heart_rate15 = _avg(health15, "avg_heart_rate")
    avg_oxygen15 = _avg(health15, "avg_oxygen")

    score = _health_score(avgs15)

    prediction = {
        "health_score": score,
        "predicted_steps": round(avgs15["steps"]),
        "predicted_distance_m": _round1(avgs15["distance_m"]),
        "predicted_calories_kcal": _round1(avgs15["calories_kcal"]),
        "predicted_avg_heart_rate": _round1(avg_heart_rate15),
        "predicted_sleep_minutes": round(avgs15["sleep_minutes"]),
        "predicted_avg_oxygen": _round1(avg_oxygen15),
        "one_line_advice": _one_line_advice(avgs15, score),
    }

    habit = {
        "summary_of_last_month": _summary_of_last_month(avgs30),
        "habit_recommendation": _habit_recommendation(health30),
    }

    return {"prediction": prediction, "habit": habit}
