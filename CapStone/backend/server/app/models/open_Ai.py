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
    당신은 노년층 사용자의 건강 데이터를 분석하는 의료 보조용 헬스케어 AI입니다.
    아래의 최근 15일 건강 데이터(요약값)를 기반으로 사용자의 건강 상태를 평가하고,
    "감점 기반 점수"와 "미래 예측값", 그리고 "한국 노년층에게 적합한 한 줄 조언"을 생성하십시오.

    데이터 컬럼은 다음 6개입니다:
    - steps: 하루 걸음 수
    - distance_m: 이동 거리 (미터)
    - calories_kcal: 소모 칼로리
    - avg_heart_rate: 평균 심박수
    - sleep_minutes: 수면 시간 (분)
    - avg_oxygen: 평균 산소포화도 (%)

    ===========================================
    📌 점수 산정 방식 (감점 기반)
    - 기본 점수: 100점
    - 아래 기준에 따라 감점을 적용하십시오.

    [걸음 수 감소 또는 매우 적음]
    - 최근 3일 평균이 전체 평균의 80% 이하: -10점
    - 하루 2000보 미만인 날이 3회 이상: -10점

    [수면 부족 또는 불규칙]
    - 평균 수면이 360분(6시간) 이하: -10점
    - 수면 변동 폭이 큰 경우(최대-최소가 120분 이상): -5점

    [심박수 비정상]
    - 평균 심박수가 90bpm 이상이거나 55bpm 이하: -10점
    - 최근 3일 연속 상승 추세: -5점

    [산소포화도 문제]
    - avg_oxygen가 94% 이하인 날이 2일 이상: -10점

    [칼로리 소비량 감소]
    - 최근 5일 평균이 앞선 10일 평균보다 20% 이상 감소: -5점

    ⚠️ 감점 기준은 모두 합산하여 총 0~100 범위로 건강 점수를 계산하십시오.

    ===========================================
    📌 예측 규칙 (15일 후)
    - 최근 15일 추세를 기반으로 선형적 예측을 하십시오.
    - 극단적 변화 대신 완만한 변화로 예측하십시오.

    예측 항목:
    - predicted_steps
    - predicted_distance_m
    - predicted_calories_kcal
    - predicted_avg_heart_rate
    - predicted_sleep_minutes
    - predicted_avg_oxygen

    ===========================================
    📌 한 줄 조언 규칙
    - 노년층이 “지금 바로 실천할 수 있는” 쉬운 조언 1가지
    - 부드럽고 위로·격려·안내 중심(위협 금지)
    - 최대 25자 이내의 짧은 문장
    예: “오늘은 10분 더 걸어보는 건 어떨까요?”

    ===========================================
    📌 출력 형식 (무조건 JSON만 출력)
    {
      "health_score": 숫자,
      "predicted_steps": 숫자,
      "predicted_distance_m": 숫자,
      "predicted_calories_kcal": 숫자,
      "predicted_avg_heart_rate": 숫자,
      "predicted_sleep_minutes": 숫자,
      "predicted_avg_oxygen": 숫자,
      "one_line_advice": "한국어 문장"
    }

    ⚠️ 반드시 JSON만 출력하십시오.
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
