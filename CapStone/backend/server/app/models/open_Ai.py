from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv
import os
import json


def run_open_ai_health_predict(ver=1, health_data=None):

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    if not health_data:
        raise ValueError("health_data가 비어 있습니다.")

    # --- 가장 안전한 프롬프트 ---
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
당신은 노년층 건강 데이터를 분석하는 의료 보조용 AI입니다.

입력되는 최근 15일간 health_data 를 기반으로 아래 JSON 구조를 정확히 채워 넣어 출력하십시오.

⚠ 반드시 JSON만 출력하고, 설명/문장/따옴표 밖 텍스트를 절대 추가하지 마십시오.
⚠ 출력은 반드시 아래와 같이 3개의 backtick 으로 감싼 JSON만 허용됩니다.

출력 형식 예시:
{
"health_score": 0,
"predicted_steps": 0,
"predicted_distance_m": 0,
"predicted_calories_kcal": 0,
"predicted_avg_heart_rate": 0,
"predicted_sleep_minutes": 0,
"predicted_avg_oxygen": 0,
"one_line_advice": "짧은 조언 문장"
}

절대 다른 텍스트를 추가하지 마십시오.
                """
            ),
            ("human", "{question}"),
        ]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,  # 안정성 우선
        disable_streaming=True,
    )

    context_str = json.dumps(health_data, ensure_ascii=False, indent=2)

    chain = {
        "context": RunnableLambda(lambda _: context_str),
        "question": RunnablePassthrough(),
    } | prompt | llm | StrOutputParser()

    question = (
        f"다음은 최근 15일간 health_data 입니다:\n{context_str}\n"
        "위 지침에 맞춰 JSON만 출력하십시오."
    )

    response = chain.invoke(question)

    # --- JSON 파싱 ---
    try:
        cleaned = response.replace("```", "").strip()
        result = json.loads(cleaned)
    except:
        result = {
            "raw_text": response,
            "error": "json_parse_failed"
        }

    return result
