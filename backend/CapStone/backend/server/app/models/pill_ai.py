# server/app/models/pill_ai.py

import os
import json
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai


def analyze_pill_image_llm(image_path: str) -> dict:
    """
    image_path: 서버에 저장된 알약 이미지 경로

    return 예시:
    {
      "pill_name": "...",
      "appearance": "...",
      "main_usage": "...",
      "warning": "...",
      "extra_advice": "..."
    }
    실패 시: {"error": "...", "raw": "..."} 형태로 리턴
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "no_api_key", "raw": "GOOGLE_API_KEY not set"}

    genai.configure(api_key=api_key)

    # 너가 현재 쓰는 모델 이름에 맞게 조정 가능 (gemini-1.5-flash / 2.0-flash 등)
    model = genai.GenerativeModel("gemini-3.6-flash")

    # 이미지 열기
    img = Image.open(image_path).convert("RGB")

    system_prompt = """
당신은 노년층을 위한 약사 보조 AI입니다.
이미지를 보고 알약의 글자, 색, 모양 등을 분석한 뒤,
아래 JSON 형식으로만 한국어로 출력하세요.

반드시 이 형식을 지키세요:

{
  "pill_name": "알약 이름(모르면 'unknown')",
  "appearance": "색, 모양, 각인 등 외형 설명",
  "main_usage": "이 약의 주요 용도 또는 추정 사용 목적 (모르면 'unknown')",
  "warning": "주의해야 할 점 또는 일반적인 복용 주의사항 (모르면 'unknown')",
  "extra_advice": "노년층에게 도움이 될 추가 조언 한 문장 (예: 복약 전 의사와 상담 권장 등)"
}

다른 문장은 절대 출력하지 말고, 반드시 위 JSON 형식만 출력하세요.
모르는 정보는 'unknown' 이라고 작성하세요.
"""

    response = model.generate_content([system_prompt, img])

    text = (response.text or "").strip()

    # ```json ... ``` 같은 거 제거
    cleaned = (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )

    try:
        data = json.loads(cleaned)
        return data
    except Exception:
        # JSON 파싱 실패 시 원문도 같이 반환
        return {"error": "json_parse_failed", "raw": text}
