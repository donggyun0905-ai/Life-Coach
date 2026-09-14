import { useState, useEffect } from 'react';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import { useSession } from '../context/SessionContext';
import { getPillList, deletePill } from '../api/pill';
import { getMe, getMeSummary } from '../api/health';
import './GuardianSharePage.css';

function GuardianSharePage() {
  const { selectedUser } = useSession();
  const nickname = selectedUser?.nickname || '홍길동';

  const [heart, setHeart] = useState(null);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);

  const [pillList, setPillList] = useState([]);
  const [pillLoading, setPillLoading] = useState(false);
  const [pillError, setPillError] = useState(null);

  const loadPillList = async (uid) => {
    if (!uid) return;
    try {
      setPillLoading(true);
      setPillError(null);

      const data = await getPillList(uid);
      const withFlags = (data || []).map((p) => ({
        ...p,
        morning: false,
        noon: false,
        night: false,
      }));
      setPillList(withFlags);
    } catch (err) {
      console.error('복약 리스트 불러오기 실패:', err);
      setPillError(err.message);
    } finally {
      setPillLoading(false);
    }
  };

  const deleteItem = async (id) => {
    if (!window.confirm('이 복약 기록을 삭제하시겠습니까?')) return;
    try {
      await deletePill(id);
      await loadPillList(selectedUser?.uid);
    } catch (err) {
      console.error('복약 기록 삭제 실패:', err);
      alert('삭제에 실패했습니다.');
    }
  };

  useEffect(() => {
    if (!selectedUser?.uid) return;

    const fetchHeartRate = async () => {
      try {
        const end = '2025-10-11T16:15:00'; // 테스트용
        const start = '2025-10-11T16:00:00'; // 테스트용

        const json = await getMe(selectedUser.uid, 'heart_rate', start, end);
        if (!json.data || json.data.length === 0) {
          setHeart(null);
          return;
        }

        const latest = json.data.reduce((a, b) => (a.id > b.id ? a : b));
        setHeart(latest.bpm);
      } catch (err) {
        console.error('심박수 불러오기 실패:', err);
      }
    };

    const fetchSummary = async () => {
      try {
        setSummaryLoading(true);
        setSummaryError(null);

        const dateStr = '2025-11-10'; // 테스트용
        const json = await getMeSummary(selectedUser.uid, dateStr, dateStr);

        if (!json.summary || json.summary.length === 0) {
          setSummary(null);
          return;
        }

        setSummary(json.summary[0]);
      } catch (err) {
        console.error('요약 데이터 불러오기 실패:', err);
        setSummaryError(err.message);
      } finally {
        setSummaryLoading(false);
      }
    };

    fetchHeartRate();
    fetchSummary();
    loadPillList(selectedUser.uid);
  }, [selectedUser]);

  let level = 'none';
  if (heart !== null) {
    if (heart >= 55 && heart <= 100) level = 'health';
    else if ((heart >= 45 && heart < 55) || (heart > 100 && heart <= 130)) level = 'warn';
    else level = 'danger';
  }

  const toggleDose = (id, field) => {
    setPillList((prev) => prev.map((p) => (p.id === id ? { ...p, [field]: !p[field] } : p)));
  };

  return (
    <div className="app-shell guardian-container">
      <AppHeader />
      <CloseButton to="/get-feedback" />

      <aside className="profile">
        <div className="avatar">👤</div>
      </aside>

      <main className="health-summary">
        <h3>● {nickname}님의 최근 건강상태</h3>

        {summaryLoading ? (
          <p className="summary-text">오늘 데이터 불러오는 중...</p>
        ) : summaryError ? (
          <p className="summary-text error">요약 데이터를 불러오지 못했습니다.</p>
        ) : summary ? (
          <div className="summary-text">
            <p>📊 오늘 걸음 수: {summary.steps?.toLocaleString()} 보</p>
            <p>🫀 평균 심박수: {summary.avg_heart_rate} bpm</p>
            <p>😴 수면 시간: {summary.sleep_minutes} 분</p>
            <p>🔥 소모 칼로리: {summary.calories_kcal} kcal</p>
          </div>
        ) : (
          <p className="summary-text">오늘 기록된 건강 데이터가 없습니다.</p>
        )}
      </main>

      <aside className="health-alerts">
        <h3>● 현재 건강 알림</h3>

        <div className={`alert-item ${level !== 'health' ? 'hide-alert' : ''}`}>
          <div className="icon-heart">💚</div>
          <div className="heart-label">건강</div>
        </div>

        <div className={`alert-item ${level !== 'warn' ? 'hide-alert' : ''}`}>
          <div className="icon-warn">⚠️</div>
          <div className="warn-label">주의</div>
        </div>

        <div className={`alert-item ${level !== 'danger' ? 'hide-alert' : ''}`}>
          <div className="icon-danger">🚨</div>
          <div className="danger-label">위험</div>
        </div>
      </aside>

      <section className="med-status">
        <h3>● 복약 상태</h3>

        {pillLoading ? (
          <p className="summary-text">복약 정보를 불러오는 중...</p>
        ) : pillError ? (
          <p className="summary-text error">복약 정보를 불러오지 못했습니다.</p>
        ) : pillList.length === 0 ? (
          <p className="summary-text">등록된 복약 정보가 없습니다.</p>
        ) : (
          <div className="pill-table">
            <div className="pill-header-row">
              <span>약 이름</span>
              <span>아침</span>
              <span>점심</span>
              <span>저녁</span>
              <span> </span>
            </div>

            {pillList.map((p) => (
              <div className="pill-row" key={p.id}>
                <span className="pill-name">{p.pill_name}</span>

                <button type="button" className={`dose-toggle ${p.morning ? 'on' : 'off'}`} onClick={() => toggleDose(p.id, 'morning')}>
                  {p.morning ? '✅' : '❌'}
                </button>
                <button type="button" className={`dose-toggle ${p.noon ? 'on' : 'off'}`} onClick={() => toggleDose(p.id, 'noon')}>
                  {p.noon ? '✅' : '❌'}
                </button>
                <button type="button" className={`dose-toggle ${p.night ? 'on' : 'off'}`} onClick={() => toggleDose(p.id, 'night')}>
                  {p.night ? '✅' : '❌'}
                </button>

                <button type="button" className="pill-delete-btn" onClick={() => deleteItem(p.id)}>
                  삭제
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default GuardianSharePage;
