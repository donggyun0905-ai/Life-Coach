import { request, withDeviceToken } from './client';

// 오늘/기간 요약 (걸음, 칼로리, 수면, 심박 등 하루 단위 집계)
export function getMeSummary(uid, startDate, endDate) {
  return request(
    `/v1/data/me-summary?start_date=${startDate}&end_date=${endDate}`,
    { headers: withDeviceToken(uid) }
  );
}

// 원시 데이터 (예: 특정 구간 심박수 샘플)
export function getMe(uid, type, startDate, endDate) {
  return request(
    `/v1/data/me?type=${type}&start_date=${startDate}&end_date=${endDate}`,
    { headers: withDeviceToken(uid) }
  );
}

// AI 예측/습관 리포트
export function getAiReport(uid) {
  return request('/v1/ai/report', { headers: withDeviceToken(uid) });
}

// 등록된 전체 uid 목록 (로그인 검증용)
export function getUids() {
  return request('/v1/data/uids');
}
