import { useState, useEffect } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import { useSession } from '../context/SessionContext';
import { getMeSummary, getAiReport } from '../api/health';
import './CheckfigPage.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

const ICONS = [
  { key: 'steps', apiKey: 'steps', label: '걸음수', emoji: '🚶' },
  { key: 'distance', apiKey: 'distance_m', label: '이동거리', emoji: '📏' },
  { key: 'calories', apiKey: 'calories_kcal', label: '칼로리', emoji: '🔥' },
  { key: 'sleep', apiKey: 'sleep_minutes', label: '수면시간', emoji: '😴' },
];

const IconButtons = ({ selected, onSelect }) => (
  <div className="icon-column" role="tablist" aria-label="데이터 항목">
    {ICONS.map((ic) => (
      <button
        key={ic.key}
        type="button"
        className={`small-icon-btn ${selected === ic.key ? 'active' : ''}`}
        onClick={() => onSelect(ic.key)}
        aria-pressed={selected === ic.key}
        title={ic.label}
      >
        <span className="emoji" aria-hidden="true">{ic.emoji}</span>
      </button>
    ))}
  </div>
);

function CheckfigPage() {
  const { selectedUser } = useSession();
  const deviceToken = selectedUser?.uid;

  const [healthData, setHealthData] = useState([]);
  const [selectedType, setSelectedType] = useState('steps');

  const [aiReport, setAiReport] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);

  useEffect(() => {
    if (!deviceToken) return;

    const fetchData = async () => {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');

      const startDate = `${year}-${month}-01`;
      const endDate = `${year}-${month}-${day}`;

      let retries = 0;
      const maxRetries = 5;
      let result = null;

      while (retries < maxRetries) {
        try {
          result = await getMeSummary(deviceToken, startDate, endDate);
          if (result && result.summary && result.summary.length > 0) break;
        } catch (err) {
          console.error('요청 에러:', err);
        }

        retries++;
        if (retries < maxRetries) {
          console.log(`데이터 없음, ${retries}번째 재시도...`);
          await new Promise((r) => setTimeout(r, 2000));
        }
      }

      if (!result || !result.summary || result.summary.length === 0) {
        setHealthData([]);
        return;
      }

      const items = result.summary
        .map((item) => {
          const date = item.date ? String(item.date).split('T')[0] : null;
          return {
            date,
            steps: item.steps ?? 0,
            distance: item.distance_m ?? item.distance ?? 0,
            calories: item.calories_kcal ?? item.calories ?? 0,
            sleep: item.sleep_minutes ?? item.sleep ?? item.total_sleep ?? item.avg_sleep_minutes ?? 0,
          };
        })
        .filter((it) => it.date);

      items.sort((a, b) => new Date(a.date) - new Date(b.date));
      setHealthData(items);

      try {
        setAiLoading(true);
        setAiError(null);
        const aiData = await getAiReport(deviceToken);
        setAiReport(aiData);
      } catch (err) {
        console.error('AI 호출 실패:', err);
        setAiError(err.message || 'AI 호출 실패');
      } finally {
        setAiLoading(false);
      }
    };

    fetchData();
  }, [deviceToken]);

  const chartData = {
    labels: healthData.map((d) => d.date),
    datasets: [
      {
        label: ICONS.find((i) => i.key === selectedType)?.label ?? selectedType,
        data: healthData.map((d) => d[selectedType]),
        borderColor: '#ff7a59',
        backgroundColor: '#ff7a59',
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#e85f3d',
      },
    ],
  };

  const chartOptions = {
    plugins: { legend: { display: false } },
    scales: { x: { display: false }, y: { display: false } },
  };

  const aiSummary = aiReport?.habit?.['summary_of_last_month'] ?? aiReport?.summary_of_last_month ?? aiReport?.prediction?.one_line_advice;
  const aiRecommendation = aiReport?.habit?.['habit_recommendation'] ?? aiReport?.habit_recommendation ?? aiReport?.recommendation;

  return (
    <div className="app-shell checkfig-container">
      <AppHeader />
      <CloseButton to="/health-feedback" label="뒤로" />

      <div className="text-wrapper">
        <h1>데이터 피드백</h1>
      </div>

      <div className="data-graphs">
        <div className="quadrant q1 card">
          <h3>🎯 목표 할당량 / 오늘 수치</h3>
          {healthData.length > 0 ? (
            <table className="goal-table">
              <tbody>
                <tr>
                  <td>목표 걸음수</td>
                  <td>4000</td>
                  <td>/</td>
                  <td>{healthData[healthData.length - 1].steps} 보</td>
                </tr>
                <tr>
                  <td>목표 이동거리</td>
                  <td>3.0 km</td>
                  <td>/</td>
                  <td>{(healthData[healthData.length - 1].distance / 1000).toFixed(2)} km</td>
                </tr>
                <tr>
                  <td>목표 칼로리</td>
                  <td>2000 kcal</td>
                  <td>/</td>
                  <td>{Number(healthData[healthData.length - 1].calories).toFixed(1)} kcal</td>
                </tr>
                <tr>
                  <td>목표 수면시간</td>
                  <td>480 min</td>
                  <td>/</td>
                  <td>{healthData[healthData.length - 1].sleep} min</td>
                </tr>
              </tbody>
            </table>
          ) : (
            <p>오늘 데이터가 없습니다.</p>
          )}
        </div>
        <div className="quadrant q2 card">
          <h3>🎯 목표 달성률</h3>
          {healthData.length > 0 ? (() => {
            const today = healthData[healthData.length - 1];
            const goals = { steps: 4000, distance: 3000, calories: 2000, sleep: 480 };

            const achievedToday = [
              today.steps >= goals.steps,
              today.distance >= goals.distance,
              today.calories >= goals.calories,
              today.sleep >= goals.sleep,
            ];
            const achievedCountToday = achievedToday.filter(Boolean).length;
            const percentageToday = Math.round((achievedCountToday / 4) * 100);

            const avgSteps = healthData.reduce((a, b) => a + b.steps, 0) / healthData.length;
            const avgDistance = healthData.reduce((a, b) => a + b.distance, 0) / healthData.length;
            const avgCalories = healthData.reduce((a, b) => a + b.calories, 0) / healthData.length;
            const avgSleep = healthData.reduce((a, b) => a + b.sleep, 0) / healthData.length;

            const achievedOverall = [
              avgSteps >= goals.steps,
              avgDistance >= goals.distance,
              avgCalories >= goals.calories,
              avgSleep >= goals.sleep,
            ];
            const achievedCountOverall = achievedOverall.filter(Boolean).length;
            const percentageOverall = Math.round((achievedCountOverall / 4) * 100);

            const pieDataToday = {
              labels: ['달성', '미달성'],
              datasets: [{ data: [achievedCountToday, 4 - achievedCountToday], backgroundColor: ['#2f6f5e', '#ffe1d6'] }],
            };
            const pieDataOverall = {
              labels: ['달성', '미달성'],
              datasets: [{ data: [achievedCountOverall, 4 - achievedCountOverall], backgroundColor: ['#ff7a59', '#ffe1d6'] }],
            };

            const pieOptions = { plugins: { legend: { position: 'bottom' } } };

            return (
              <div className="q2-inner">
                <p className="today">오늘 달성률: {percentageToday}%</p>
                <Doughnut data={pieDataToday} options={pieOptions} />

                <p className="all">전체 기간 달성률: {percentageOverall}%</p>
                <Doughnut data={pieDataOverall} options={pieOptions} />
              </div>
            );
          })() : (
            <p>데이터가 없습니다.</p>
          )}
        </div>
        <div className="quadrant q3 card">
          <h3>📊 최근 변화</h3>
          <div className="q3-inner">
            <IconButtons selected={selectedType} onSelect={setSelectedType} />
            <div className="selected-info">
              <strong>{ICONS.find((i) => i.key === selectedType)?.label ?? selectedType}</strong>
            </div>
          </div>
          <div className="mini-chart">
            {healthData.length > 0 ? <Line data={chartData} options={chartOptions} /> : null}
          </div>
        </div>
        <div className="quadrant q4 card">
          <h3>📡 AI 분석 결과</h3>

          {aiLoading && <p>AI 분석 중...</p>}
          {aiError && <p style={{ color: 'red' }}>AI 에러: {aiError}</p>}

          {aiReport ? (
            <>
              {aiSummary && (
                <div className="ai-box" style={{ whiteSpace: 'pre-wrap', marginBottom: 8 }}>
                  <strong>분석결과</strong>
                  <div style={{ marginTop: 6 }}>{aiSummary}</div>
                </div>
              )}

              {aiRecommendation && (
                <div className="ai-box" style={{ whiteSpace: 'pre-wrap', marginBottom: 8 }}>
                  <strong>추천</strong>
                  <div style={{ marginTop: 6 }}>{aiRecommendation}</div>
                </div>
              )}
            </>
          ) : (
            !aiLoading && <p>AI 분석 결과가 없습니다.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default CheckfigPage;
