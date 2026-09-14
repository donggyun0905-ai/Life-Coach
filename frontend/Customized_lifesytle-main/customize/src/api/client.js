// 백엔드 서버 주소 + 인증 토큰을 한 곳에서 관리한다.
// (이전에는 컴포넌트 7~8곳에 이 값이 그대로 복붙되어 있었다.)
// .env / .env.local 의 REACT_APP_API_BASE_URL로 로컬 백엔드와 배포 백엔드를 전환한다.
export const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://capstone-lozi.onrender.com';
const API_TOKEN = 'capstone_token_0905';

export function withDeviceToken(uid) {
  return { 'X-DEVICE-TOKEN': uid };
}

export function withBearer() {
  return { Authorization: `Bearer ${API_TOKEN}` };
}

/**
 * fetch 기반 공용 요청 헬퍼.
 * - JSON 바디는 자동 직렬화
 * - 실패 시 상태코드 + 본문을 담은 Error를 던진다
 */
export async function request(path, { method = 'GET', headers = {}, body } = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json', ...headers } : headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText}${text ? ` - ${text}` : ''}`);
  }

  if (res.status === 204) return null;
  return res.json();
}
