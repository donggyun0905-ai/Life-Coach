# check_data.py
import requests
from datetime import datetime, timedelta

BASE_URL = "https://capstone-lozi.onrender.com/v1/data"
DAYS = 21
TYPES = ["steps","heartrate","distance","calories","oxygen","sleep","exercise"]

def list_uids():
    r = requests.get(f"{BASE_URL}/uids", timeout=30)
    r.raise_for_status()
    return r.json()

def fetch(uid, type_=None, start=None, end=None):
    params = {}
    if type_: params["type"] = type_
    if start: params["start"] = start
    if end: params["end"] = end
    r = requests.get(f"{BASE_URL}/{uid}", params=params, timeout=60)
    # 404면 해당 기간/타입 데이터 없음
    if r.status_code == 404:
        return {"uid": uid, "type": type_ or "all", "data": []}
    r.raise_for_status()
    return r.json()

def iso(dt): return dt.isoformat(timespec="seconds")

def summarize_for_uid(uid):
    end = datetime.now()
    start = end - timedelta(days=DAYS)
    start_s, end_s = iso(start), iso(end)

    print(f"\n====== UID: {uid} | 기간: {start_s} ~ {end_s} ======")
    # 전체 한 번에 보고 싶으면 아래 한 줄로도 가능
    # all_data = fetch(uid, start=start_s, end=end_s)
    # print(all_data)

    # 타입별 요약
    for t in TYPES:
        res = fetch(uid, type_=t, start=start_s, end=end_s)
        rows = res.get("data", []) if "data" in res else res.get(t, [])
        cnt = len(rows)
        print(f"[{t:11}] {cnt:4} 건")

        # 샘플 2줄만 깔끔하게 보여주기
        for i, row in enumerate(rows[:2]):
            # 컬럼 이름이 모델마다 달라서 공통적으로 유용한 것만 표시
            ts = row.get("time") or row.get("start_time") or row.get("end_time")
            # 값 필드 예시 추출
            val = (
                row.get("count")
                or row.get("bpm")
                or row.get("distance")
                or row.get("calories_kcal")
                or row.get("percentage")
                or row.get("exercise_type")
                or row.get("title")
                or row.get("stage")
            )
            print(f"   - sample[{i}]: time={ts} value={val}")
    print("=============================================")

def main():
    try:
        uids = list_uids()
    except requests.HTTPError as e:
        print("❌ UID 목록 조회 실패:", e)
        return
    except Exception as e:
        print("❌ 네트워크 오류:", e)
        return

    if not uids:
        print("⚠️ UID가 없습니다. 앱에서 데이터를 한 번 전송해 주세요.")
        return

    print("✅ 서버에 등록된 UID 목록:", uids)

    # 모든 UID에 대해 요약 출력 (필요하면 한 개만 보고 싶으면 uids[:1])
    for uid in uids:
        try:
            summarize_for_uid(uid)
        except requests.HTTPError as e:
            print(f"❌ {uid} 조회 실패:", e)
        except Exception as e:
            print(f"❌ {uid} 처리 중 오류:", e)

if __name__ == "__main__":
    main()
