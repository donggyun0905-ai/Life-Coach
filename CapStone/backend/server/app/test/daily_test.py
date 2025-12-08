import os
from dotenv import load_dotenv
from ..models.open_Ai import run_open_ai_full_report

# smith.env 절대 경로 지정 (현재 파일 기준)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(FILE_DIR, "smith.env")

load_dotenv(ENV_PATH)

print("KEY:", os.getenv("GOOGLE_API_KEY"))

# 테스트용 가짜 데이터
health15 = [
    {"date": "2025-01-01", "steps": 5000, "distance_m": 3200,
     "calories_kcal": 200, "avg_heart_rate": 72, "sleep_minutes": 420, "avg_oxygen": 96}
]

health30 = [
    {"date": "2025-01-01", "steps": 5000, "distance_m": 3200,
     "calories_kcal": 200, "avg_heart_rate": 72, "sleep_minutes": 420, "avg_oxygen": 96}
]

result = run_open_ai_full_report(health15, health30)
print(result)
