# 라이프코치 (Life Coach)

어르신들을 위한 헬스케어 소프트웨어 — Health Connect 기반 건강 데이터 수집, AI 기반 피드백, 복약 관리, 보호자 공유 기능을 제공하는 캡스톤 프로젝트.

## 구조

```
android/    걸음/심박/수면 등 Health Connect 데이터를 15분 주기로 수집해 백엔드로 전송 (Kotlin, WorkManager, Retrofit)
backend/    데이터 수집/조회 API, 복약 사진 분석, 건강 리포트 생성 (FastAPI, SQLAlchemy, PostgreSQL)
frontend/   보호자/사용자용 웹 대시보드 — 건강 데이터 확인, AI 리포트, 복약 관리 (React, React Router)
```

## 기술 스택

- **Android**: Kotlin, Health Connect API, WorkManager, Retrofit
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Google Gemini Vision(복약 사진 분석)
- **Frontend**: React, React Router, Chart.js

## 주요 기능

- Health Connect로 걸음/심박/거리/칼로리/수면/운동/산소포화도 자동 수집
- 최근 15/30일 데이터 기반 통계 예측 + 규칙 기반 건강 피드백 (외부 AI 비용 없이 동작)
- 알약 사진을 찍으면 AI가 이름/효능/주의사항 분석
- 보호자-사용자 역할 분리, 실시간 건강 상태 공유

## 로컬 실행

### Backend
```bash
cd backend/CapStone/backend/server
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL, GOOGLE_API_KEY 채우기
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend/Customized_lifesytle-main/customize
npm install
cp .env.example .env.local
npm start
```

### Android
Android Studio에서 `android/Myapplication - 브릿지 파일` 열고 실행, 또는:
```bash
cd "android/Myapplication - 브릿지 파일"
./gradlew installDebug
```
