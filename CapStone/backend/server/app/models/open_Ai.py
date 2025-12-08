from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os, json


def run_open_ai_full_report(health15, health30):
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    # 2개 데이터 묶기
    context = {
        "last_15_days": health15,
        "last_30_days": health30
    }
    context_str = json.dumps(context, esure_ascii=False, indent=2)

    system_prompt = """
당신은 노년층 건강 분석을 수행하는 AI입니다.

입력: 최근 15일 요약 데이터 + 최근 30일 요약 데이터

출력:
1) JSON만 출력
2) 최상위 2개의 key 포함 → prediction, habit

[prediction]
- health_score
- predicted_steps
- predicted_distance_m
- predicted_calories_kcal
- predicted_avg_heart_rate
- predicted_sleep_minutes
- predicted_avg_oxygen
- one_line_advice

[habit]
- summary_of_last_month
- habit_recommendation

설명 없이 JSON만 출력하십시오.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "다음은 건강 데이터입니다:\n{context}\n\nJSON만 출력하십시오.")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        disable_streaming=True,
        max_retries=0
    )

    chain = prompt | llm | StrOutputParser()

    # -------------------- AI 호출 안전처리 --------------------
    try:
        response = chain.invoke({"context": context_str})

    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            return {
                "error": "quota_exceeded",
                "message": "AI 모델 무료 사용량이 소진되었습니다. 결제를 활성화해야 합니다."
            }
        return {
            "error": "ai_call_failed",
            "detail": str(e)
        }

    # -------------------- 응답에서 에러 텍스트 감지 --------------------
    if any(x in response.lower() for x in ["quota", "exceeded", "429"]):
        return {
            "error": "quota_exceeded",
            "message": "AI 모델 호출이 차단되었습니다.",
            "raw_text": response
        }

    # -------------------- JSON 파싱 --------------------
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except:
        return {
            "error": "json_parse_failed",
            "raw_text": response
        }
