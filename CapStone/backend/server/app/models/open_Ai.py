from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os, json

def run_open_ai_habit_recommendation(ver=1, monthly_data=None):

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    if not monthly_data:
        raise ValueError("monthly_data가 비어 있습니다. (최근 한 달 데이터 필요)")

    context_str = json.dumps(monthly_data, ensure_ascii=False, indent=2)

    system_prompt = """
당신은 노년층의 한 달 건강 데이터를 기반으로 맞춤형 생활 습관을 추천하는 AI입니다.

출력 규칙:
1) 반드시 JSON만 출력할 것
2) JSON 외 텍스트 금지
3) JSON은 아래 key를 반드시 포함해야 함:

- habit_recommendation
- summary_of_last_month

각 설명은 자연어 문장 1~3줄 이내로 작성.
recommendation은 ‘생활 습관 개선 전략’을 전달해야 함.
summary_of_last_month는 ‘한 달간 건강 경향 요약’을 나타내야 함.

예시 문장은 설명용이며 실제 출력 JSON에 포함하면 안 됨.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "다음은 최근 30일 간의 건강 데이터입니다:\n{context}\n\nJSON만 출력하세요.")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        disable_streaming=True,
    )

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": context_str})

    # JSON 파싱
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except:
        return {
            "error": "json_parse_failed",
            "raw_text": response
        }


def run_open_ai_health_predict(ver=1, health_data=None):

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    if not health_data:
        raise ValueError("health_data가 비어 있습니다.")

    context_str = json.dumps(health_data, ensure_ascii=False, indent=2)

    system_prompt = """
당신은 노년층 건강 데이터를 분석하는 의료 보조용 AI입니다.

출력 규칙:
1) 반드시 JSON만 출력할 것
2) JSON 외의 텍스트(설명, 문장, 인사말) 절대 금지
3) JSON 형식은 다음 key 들을 포함해야 함:

- health_score
- predicted_steps
- predicted_distance_m
- predicted_calories_kcal
- predicted_avg_heart_rate
- predicted_sleep_minutes
- predicted_avg_oxygen
- one_line_advice

각 필드는 숫자 또는 문자열로 채워야 합니다.
JSON 예시는 말로만 설명하며, 실제 예시는 제공하지 않습니다.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "다음은 최근 15일간 health_data 입니다:\n{context}\n\n위 지침에 맞춰 JSON만 출력하십시오.")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
        disable_streaming=True,
    )

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": context_str})

    # JSON 파싱
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except:
        return {
            "error": "json_parse_failed",
            "raw_text": response
        }
