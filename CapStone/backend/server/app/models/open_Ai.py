from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os, json


def run_open_ai_full_report(health15, health30):
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    # 2개 데이터 한번에 JSON 으로 묶기
    context = {
        "last_15_days": health15,
        "last_30_days": health30
    }
    context_str = json.dumps(context, ensure_ascii=False, indent=2)

    system_prompt = """
당신은 노년층 건강 분석을 수행하는 AI입니다.

입력은 두 가지 데이터 세트입니다:
1) 최근 15일 요약 데이터 (예측용)
2) 최근 30일 요약 데이터 (생활 습관 분석용)

출력 규칙:
1) 반드시 JSON만 출력
2) JSON 외 문장 출력 금지
3) JSON은 다음 구조를 반드시 포함해야 함:

{
  "prediction": {
      "health_score": 숫자,
      "predicted_steps": 숫자,
      "predicted_distance_m": 숫자,
      "predicted_calories_kcal": 숫자,
      "predicted_avg_heart_rate": 숫자,
      "predicted_sleep_minutes": 숫자,
      "predicted_avg_oxygen": 숫자,
      "one_line_advice": "문장"
  },
  "habit": {
      "summary_of_last_month": "문장",
      "habit_recommendation": "문장"
  }
}

절대 다른 텍스트를 추가하지 말고 정확히 JSON만 출력하시오.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "다음은 최근 15일 & 30일 건강 데이터입니다:\n{context}\n\n위 JSON 형식 그대로 출력하십시오.")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        disable_streaming=True,
        max_retries=0
    )

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": context_str})

    # 쿼터 초과 감지
    if "quota" in response.lower() or "exceeded" in response.lower() or "429" in response:
        return {
            "error": "quota_exceeded",
            "message": "AI 무료 사용량이 소진되었습니다. 유료 결제를 활성화해야 계속 사용할 수 있습니다."
        }

    # JSON 파싱
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except:
        return {
            "error": "json_parse_failed",
            "raw_text": response
        }
