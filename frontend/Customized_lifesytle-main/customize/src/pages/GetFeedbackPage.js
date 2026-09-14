import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import { useSession } from '../context/SessionContext';
import { getAiReport, getMeSummary } from '../api/health';
import './GetFeedbackPage.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);

const MetricRow = ({ emoji, label, value, unit, direction }) => {
  const up = direction === 'up';
  const equal = direction === 'equal';
  const color = equal ? '#8a7c6f' : up ? '#2f6f5e' : '#e2453c';
  const arrow = equal ? '—' : up ? '▲' : '▼';

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 4px', borderBottom: '1px solid #efe2d2' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <span style={{ fontSize: 38, width: 56, height: 56, borderRadius: '50%', background: '#fff1e8', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>{emoji}</span>
        <div>
          <div style={{ fontWeight: 800, fontSize: 16 }}>{label}</div>
          <div style={{ fontSize: 13, color: '#8a7c6f' }}>{value !== null && value !== undefined ? `${value} ${unit ?? ''}` : '데이터 없음'}</div>
        </div>
      </div>

      <div style={{ fontSize: 26, color, fontWeight: 800 }}>{arrow}</div>
    </div>
  );
};

const TRANSITION_MS = 2000;

function GetFeedbackPage() {
  const navigate = useNavigate();
  const { selectedUser } = useSession();
  const deviceToken = selectedUser?.uid;

  const [expanded, setExpanded] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [healthData, setHealthData] = useState([]);
  const [loadingHealth, setLoadingHealth] = useState(false);

  const [detailOpen, setDetailOpen] = useState(false);
  const frameRef = useRef(null);

  useEffect(() => {
    const fetchAi = async () => {
      if (!deviceToken) { setError('사용자가 선택되지 않았습니다'); return; }
      setLoading(true); setError(null);
      try {
        const json = await getAiReport(deviceToken);
        setData(json);
      } catch (err) {
        console.error('AI 호출 실패:', err);
        setError(err.message || 'AI 호출 실패');
      } finally { setLoading(false); }
    };
    fetchAi();
  }, [deviceToken]);

  const fetchHealthSummary = async () => {
    if (healthData && healthData.length > 0) return;
    setLoadingHealth(true);
    try {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      const startDate = `${year}-${month}-01`;
      const endDate = `${year}-${month}-${day}`;

      const json = await getMeSummary(deviceToken, startDate, endDate);

      const items = (json.summary || []).map(item => {
        const date = item.date ? String(item.date).split('T')[0] : null;
        return {
          date,
          steps: item.steps ?? 0,
          distance: item.distance_m ?? item.distance ?? 0,
          calories: item.calories_kcal ?? item.calories ?? 0,
          sleep: item.sleep_minutes ?? item.sleep ?? item.total_sleep ?? item.avg_sleep_minutes ?? 0,
          heart: item.avg_heart_rate ?? item.predicted_avg_heart_rate ?? null,
        };
      }).filter(Boolean).sort((a, b) => new Date(a.date) - new Date(b.date));

      setHealthData(items);
    } catch (err) {
      console.error('health summary fetch failed', err);
    } finally { setLoadingHealth(false); }
  };

  const healthScore = data?.health_score ?? data?.prediction?.health_score ?? data?.score ?? '—';
  const oneLineAdvice = data?.one_line_advice ?? data?.prediction?.one_line_advice ?? data?.message ?? '피드백이 없습니다';
  const pred = data?.prediction ?? data ?? {};
  const pSteps = pred?.predicted_steps ?? pred?.steps ?? null;
  const pSleep = pred?.predicted_sleep_minutes ?? pred?.predicted_sleep ?? pred?.sleep ?? null;
  const pHeart = pred?.predicted_avg_heart_rate ?? pred?.predicted_avg_heartRate ?? pred?.avg_heart_rate ?? pred?.heart_rate ?? null;
  const pCalories = pred?.predicted_calories_kcal ?? pred?.predicted_calories ?? pred?.calories_kcal ?? pred?.calories ?? null;

  const goals = { steps: 4000, sleep: 480, heart: 70, calories: 2000 };
  const getDirection = (value, goal) => {
    if (value === null || value === undefined) return 'equal';
    if (value > goal) return 'up';
    if (value < goal) return 'down';
    return 'equal';
  };

  useEffect(() => {
    const el = frameRef.current;
    if (!el) return;
    el.style.overflow = 'hidden';
    el.style.maxHeight = '0px';
    el.style.opacity = '0';
    el.style.transition = `max-height ${TRANSITION_MS}ms ease, opacity ${Math.max(TRANSITION_MS - 40, 200)}ms ease`;
  }, []);

  const waitForTransition = (el, timeout = TRANSITION_MS + 120) => {
    return new Promise(resolve => {
      if (!el) return resolve();
      let done = false;
      const handler = (e) => {
        if (e.propertyName !== 'max-height' && e.propertyName !== 'opacity') return;
        if (done) return;
        done = true;
        el.removeEventListener('transitionend', handler);
        resolve();
      };
      el.addEventListener('transitionend', handler);
      setTimeout(() => {
        if (done) return;
        done = true;
        el.removeEventListener('transitionend', handler);
        resolve();
      }, timeout);
    });
  };

  const openFrame = () => {
    const el = frameRef.current;
    if (!el) { setExpanded(true); return; }
    el.style.overflow = 'hidden';
    el.style.transition = `max-height ${TRANSITION_MS}ms ease, opacity ${Math.max(TRANSITION_MS - 40, 200)}ms ease`;
    void el.offsetHeight;
    el.style.maxHeight = el.scrollHeight + 'px';
    el.style.opacity = '1';
    setExpanded(true);
    const onEnd = (e) => {
      if (e.propertyName !== 'max-height') return;
      el.style.overflow = 'visible';
      el.removeEventListener('transitionend', onEnd);
    };
    el.addEventListener('transitionend', onEnd);
  };

  const closeFrame = () => {
    const el = frameRef.current;
    if (!el) { setExpanded(false); return; }
    el.style.overflow = 'hidden';
    el.style.transition = `max-height ${TRANSITION_MS}ms ease, opacity ${Math.max(TRANSITION_MS - 40, 200)}ms ease`;
    el.style.maxHeight = el.scrollHeight + 'px';
    void el.offsetHeight;
    el.style.maxHeight = '0px';
    el.style.opacity = '0';
    const onEnd = (e) => {
      if (e.propertyName !== 'max-height') return;
      setExpanded(false);
      el.removeEventListener('transitionend', onEnd);
    };
    el.addEventListener('transitionend', onEnd);
  };

  const toggleExpandedByText = () => {
    if (!expanded) openFrame();
    else {
      setDetailOpen(false);
      closeFrame();
    }
  };

  const onDetailToggle = async () => {
    const willOpen = !detailOpen;
    if (willOpen) {
      if (!expanded) openFrame();
      await waitForTransition(frameRef.current);
      await fetchHealthSummary();
      setDetailOpen(true);
      setTimeout(() => frameRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 60);
    } else {
      setDetailOpen(false);
    }
  };

  const labels = healthData.length > 0 ? healthData.map(d => d.date) : ['최근'];
  const stepsData = healthData.length > 0 ? healthData.map(d => d.steps) : [pSteps ?? 0];
  const sleepData = healthData.length > 0 ? healthData.map(d => d.sleep) : [pSleep ?? 0];
  const heartData = healthData.length > 0 ? healthData.map(d => d.heart ?? 0) : [pHeart ?? 0];
  const caloriesData = healthData.length > 0 ? healthData.map(d => d.calories) : [pCalories ?? 0];

  const sleepDonut = { labels, datasets: [{ data: sleepData, backgroundColor: ['#2f6f5e', '#6fa696', '#c7ddd6'] }] };
  const caloriesDonut = { labels, datasets: [{ data: caloriesData, backgroundColor: ['#ff7a59', '#ffab8f', '#ffe1d6'] }] };
  const stepsBar = { labels, datasets: [{ label: '걸음', data: stepsData, backgroundColor: ['#ff7a59', '#e85f3d'] }] };
  const heartLine = { labels, datasets: [{ label: '심박수', data: heartData, borderColor: '#d99a12', backgroundColor: '#d99a12', fill: false, tension: 0.3, pointRadius: 4 }] };

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { enabled: true } },
    scales: { x: { display: true }, y: { display: true } },
  };

  return (
    <div className={`app-shell feedback-container ${expanded ? 'expanded' : ''}`}>
      <AppHeader />
      <CloseButton />

      {loading ? <h1 className="feedback-score">로딩 중...</h1> :
        error ? <h1 className="feedback-score" style={{ color: 'red' }}>에러: {error}</h1> :
        <h1 className="feedback-score">예상 점수 : <span>{healthScore}</span></h1>
      }

      <div className={`feedback-message-box ${expanded ? 'expanded' : ''}`}>
        <div className={`triangle-marker ${expanded ? 'down' : 'right'}`} />
        <p className="feedback-message" aria-expanded={expanded} onClick={toggleExpandedByText}>"{oneLineAdvice}"</p>
      </div>

      <div
        ref={frameRef}
        className={`transform-frame ${expanded ? 'active' : ''}`}
        aria-hidden={!expanded}
        style={{ padding: 12, position: 'relative' }}
      >
        <div className="transform-emoji">
          <MetricRow emoji="😴" label="수면" value={pSleep} unit="min" direction={getDirection(pSleep, goals.sleep)} />
          <MetricRow emoji="👣" label="걸음 수" value={pSteps} unit="걸음" direction={getDirection(pSteps, goals.steps)} />
          <MetricRow emoji="❤️" label="심박수" value={pHeart} unit="bpm" direction={getDirection(pHeart, goals.heart)} />
          <MetricRow emoji="🍽️" label="칼로리" value={pCalories} unit="kcal" direction={getDirection(pCalories, goals.calories)} />
        </div>

        <div style={{ marginTop: 12 }}>
          <button className="dashboard-btn" onClick={onDetailToggle} aria-expanded={detailOpen}>{detailOpen ? '상세 닫기' : '상세보기'}</button>
        </div>

        {detailOpen && (
          <div style={{
            marginTop: 18,
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 18,
            alignItems: 'start'
          }}>
            <div style={{ background: '#fff', padding: 12, borderRadius: 8, minHeight: 320 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>수면 시간</div>
              {loadingHealth ? <div>로딩...</div> : <div style={{ height: 260 }}><Doughnut data={sleepDonut} options={commonOptions} /></div>}
            </div>

            <div style={{ background: '#fff', padding: 12, borderRadius: 8, minHeight: 320 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>걸음 수</div>
              {loadingHealth ? <div>로딩...</div> : <div style={{ height: 260 }}><Bar data={stepsBar} options={commonOptions} /></div>}
            </div>

            <div style={{ background: '#fff', padding: 12, borderRadius: 8, minHeight: 320 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>심박수</div>
              {loadingHealth ? <div>로딩...</div> : <div style={{ height: 260 }}><Line data={heartLine} options={commonOptions} /></div>}
            </div>

            <div style={{ background: '#fff', padding: 12, borderRadius: 8, minHeight: 320 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>칼로리</div>
              {loadingHealth ? <div>로딩...</div> : <div style={{ height: 260 }}><Doughnut data={caloriesDonut} options={commonOptions} /></div>}
            </div>
          </div>
        )}
      </div>

      <button className="share-btn" onClick={() => navigate('/guardian-share')}>공유</button>
    </div>
  );
}

export default GetFeedbackPage;
