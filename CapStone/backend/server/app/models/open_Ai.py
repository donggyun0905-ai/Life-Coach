from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
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
        raise ValueError("health_data가 비어 있습니다. 15일치 데이터를 전달해주세요.")

    # 안전한 시스템 프롬프트
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
당신은 노년층 사용자의 건강 데이터를 분석하는 의료 보조 헬스케어 AI입니다.

입력으로 제공되는 최근 15일간 health_data를 기반으로 다음 8개 필드를 포함한 JSON 텍스트를 출력하십시오.

필드:
- health_score
- predicted_steps
- predicted_distance_m
- predicted_calories_kcal
- predicted_avg_heart_rate
- predicted_sleep_minutes
- predicted_avg_oxygen
- one_line_advice

출력은 반드시 아래 형식을 따라야 하며, 설명 문구 없이 JSON만 출력하십시오:

{
  "health_score": 숫자,
  "predicted_steps": 숫자,
  "predicted_distance_m": 숫자,
  "predicted_calories_kcal": 숫자,
  "predicted_avg_heart_rate": 숫자,
  "predicted_sleep_minutes": 숫자,
  "predicted_avg_oxygen": 숫자,
  "one_line_advice": "문장"
}
"""
            ),
            ("human", "{question}"),
        ]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        disable_streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    context_str = json.dumps(health_data, ensure_ascii=False, indent=2)

    chain = {
        "context": RunnableLambda(lambda _: context_str),
        "question": RunnablePassthrough(),
    } | prompt | llm | StrOutputParser()

    question = (
        f"다음은 최근 15일간 건강데이터입니다:\n{context_str}\n"
        "이 정보를 기반으로 미래 예측값을 JSON으로 출력하십시오."
    )

    response = chain.invoke(question)

    # JSON 파싱
    try:
        result = json.loads(response)
    except:
        # 혹시 줄바꿈/쉼표 오류 발생 시 보정
        cleaned = response.strip()
        cleaned = cleaned.replace("\n", "").replace(",}", "}")
        try:
            result = json.loads(cleaned)
        except:
            result = {
                "raw_text": response,
                "error": "json_parse_failed"
            }

    return result
