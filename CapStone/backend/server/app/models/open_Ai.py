from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv
import os
import json


def run_open_ai_health_predict(ver=1, health_data=None):
    """
    📊 15일간의 건강 데이터를 기반으로 15일 후 예상 건강 점수와 한 줄 조언을 생성하는 함수
    - 대상: 노년층 사용자
    - 입력: health_data (list[dict])
        예시:
        [
            {"date": "2025-10-20", "steps": 8230, "sleep_minutes": 410, "avg_heart_rate": 78, "calories_kcal": 320, "avg_oxygen": 97.5},
            {"date": "2025-10-21", "steps": 8120, "sleep_minutes": 430, "avg_heart_rate": 80, "calories_kcal": 310, "avg_oxygen": 96.8},
            ...
        ]
    - 출력: JSON 형태의 예측 점수와 한국어 조언
    """
    # ✅ 환경 변수 불러오기
    load_dotenv(dotenv_path="smith.env")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", "불러옴" if google_api_key else "❌ 없음")

    # ✅ 건강 데이터 확인
    if not health_data:
        raise ValueError("health_data가 비어 있습니다. 15일치 데이터를 전달해주세요.")

    # ✅ Prompt 구성
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
당신은 노년층 사용자의 건강 데이터를 분석하고 미래 상태를 예측하는 헬스케어 AI 어시스턴트입니다.

다음은 사용자의 최근 15일간 건강 데이터입니다.
걸음 수(steps), 평균 심박수(avg_heart_rate), 수면 시간(sleep_minutes), 칼로리(calories_kcal) 및 산소포화도(avg_oxygen)를 참고하여
향후 15일 후의 예상 건강 상태를 분석하고, 다음과 같은 JSON으로 출력하세요.

출력 형식(JSON):
{
  "health_score": (0~100 사이의 점수),
  "predicted_steps": (15일 후 예상 걸음 수),
  "predicted_sleep_hours": (15일 후 예상 수면 시간, 시간 단위),
  "predicted_heart_rate": (15일 후 예상 평균 심박수),
  "predicted_calories": (15일 후 예상 칼로리 소비량),
  "one_line_advice": "노년층을 위한 한 줄 건강 조언 (한국어, 따뜻하고 실천 가능한 말투)"
}

점수 산정 기준:
- 걸음 수가 안정적으로 유지되고 증가 추세면 +10점
- 평균 심박수가 60~90bpm 사이면 +10점
- 수면 시간이 6~8시간이면 +10점
- 칼로리 소비량이 꾸준하면 +10점
- 데이터가 불규칙하거나 감소 추세면 -점

출력은 반드시 JSON 형식으로, 한국어 조언을 포함해야 합니다.
                """,
            ),
            ("human", "{question}"),
        ]
    )

    # ✅ Gemini 모델 초기화
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,  # 조언이 너무 기계적이지 않도록 약간의 창의성
        disable_streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    # ✅ health_data를 문자열(JSON)로 변환
    context_str = json.dumps(health_data, ensure_ascii=False, indent=2)

    # ✅ LangChain 실행 체인
    chain = {
        "context": RunnableLambda(lambda _: context_str),
        "question": RunnablePassthrough(),
    } | prompt | llm | StrOutputParser()

    # ✅ 질문 설정
    if ver == 1:
        question = (
            f"다음은 사용자의 최근 15일 건강 데이터입니다:\n{context_str}\n"
            "이 데이터를 기반으로 15일 후의 건강 점수와 한 줄 조언을 예측해주세요."
        )
    else:
        question = (
            f"{context_str}\n"
            "데이터 추세를 분석하여 건강 점수와 조언을 출력하세요."
        )

    # ✅ Gemini 호출
    response = chain.invoke(question)

    # ✅ Gemini 응답 JSON 변환 시도
    try:
        result = json.loads(response)
    except Exception:
        result = {"raw_text": response, "message": "⚠️ JSON 변환 실패 (모델이 텍스트로 응답했을 수 있습니다.)"}

    return result
