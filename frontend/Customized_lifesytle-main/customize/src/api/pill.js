import axios from 'axios';
import { BASE_URL, withBearer } from './client';

// 알약 사진 업로드 → LLM 분석 결과 반환
export async function uploadPillImage(uid, file) {
  const formData = new FormData();
  formData.append('uid', uid);
  formData.append('file', file);

  const res = await axios.post(`${BASE_URL}/v1/ingest/pill_image`, formData, {
    headers: { ...withBearer(), 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

// 사용자별 복약 기록 조회
export async function getPillList(uid) {
  const res = await axios.get(`${BASE_URL}/v1/ingest/pill_list?uid=${uid}`, {
    headers: { accept: 'application/json', ...withBearer() },
  });
  return res.data;
}

// 복약 기록 삭제
export async function deletePill(id) {
  const res = await axios.delete(`${BASE_URL}/v1/ingest/pill/${id}`, {
    headers: withBearer(),
  });
  return res.data;
}
