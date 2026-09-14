import { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import { useSession } from '../context/SessionContext';
import { getMeSummary } from '../api/health';
import './CheckDataPage.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// 운동과 심박수 제외
const METRICS = [
  { key: 'steps', apiKey: 'steps', label: '걸음수' },
  { key: 'distance', apiKey: 'distance_m', label: '이동거리' },
  { key: 'calories', apiKey: 'calories_kcal', label: '칼로리' },
  { key: 'sleep', apiKey: 'sleep_minutes', label: '수면시간' },
];

function CheckDataPage() {
  const { selectedUser } = useSession();
  const deviceToken = selectedUser?.uid;

  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [day, setDay] = useState('');
  const [chartData, setChartData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('steps');
  const [showMetrics, setShowMetrics] = useState(false);

  const handleSearch = async (metricKey = selectedMetric) => {
    if (!deviceToken) {
      setErrorMsg('사용자가 선택되지 않았습니다');
      setChartData(null);
      return;
    }

    const inputDate = new Date(`${year}-${month}-${day}`);
    if (isNaN(inputDate)) {
      setErrorMsg('올바른 날짜를 입력하세요');
      setChartData(null);
      return;
    }

    // 시작 날짜는 그 달의 첫날
    const startDate = new Date(inputDate.getFullYear(), inputDate.getMonth(), 1);
    const startISO = startDate.toISOString().split('T')[0];
    const endISO = inputDate.toISOString().split('T')[0];

    const metric = METRICS.find((m) => m.key === metricKey);
    if (!metric) {
      setErrorMsg('잘못된 항목 선택');
      return;
    }

    let retries = 0;
    const maxRetries = 5;
    let result = null;

    while (retries < maxRetries) {
      try {
        result = await getMeSummary(deviceToken, startISO, endISO);
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
      setChartData(null);
      setErrorMsg('데이터 없음');
      return;
    }

    const items = result.summary
      .map((item) => {
        const date = item.date ? String(item.date).split('T')[0] : null;
        let value = item[metric.apiKey] ?? 0;
        if (metric.key === 'distance' && value < 50) value = value * 1000;
        return { date, value };
      })
      .filter((it) => it.date);

    const uniqueItems = Array.from(new Map(items.map((it) => [it.date, it])).values());
    uniqueItems.sort((a, b) => new Date(a.date) - new Date(b.date));

    if (uniqueItems.length === 0) {
      setChartData(null);
      setErrorMsg('데이터 없음');
      return;
    }

    setChartData({
      labels: uniqueItems.map((it) => it.date),
      datasets: [
        {
          label: metric.label,
          data: uniqueItems.map((it) => it.value),
          borderColor: '#ff7a59',
          backgroundColor: '#ff7a59',
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: '#e85f3d',
        },
      ],
    });
    setErrorMsg('');
  };

  const handleMetricClick = (key) => {
    setSelectedMetric(key);
    handleSearch(key);
  };

  return (
    <div className="app-shell checkdata-container">
      <AppHeader />
      <CloseButton to="/health-feedback" label="뒤로" />

      <div className="text-wrapper">
        <h1>데이터 확인</h1>
      </div>

      <section className="date-controls">
        <div className="date-fields">
          <div className="data-field">
            <input type="text" inputMode="numeric" placeholder="년" value={year} onChange={(e) => setYear(e.target.value)} />
          </div>
          <span className="date-sep">-</span>
          <div className="data-field">
            <input type="text" inputMode="numeric" placeholder="월" value={month} onChange={(e) => setMonth(e.target.value)} />
          </div>
          <span className="date-sep">-</span>
          <div className="data-field">
            <input type="text" inputMode="numeric" placeholder="일" value={day} onChange={(e) => setDay(e.target.value)} />
          </div>
        </div>

        <div className="control-row">
          <div className="metrics-wrap">
            <button
              type="button"
              className={`toggle-metrics-btn ${showMetrics ? 'open' : ''}`}
              aria-expanded={showMetrics}
              onClick={() => setShowMetrics((s) => !s)}
            >
              항목 ▾
            </button>

            <section className={`metric-buttons ${showMetrics ? 'open' : ''}`} aria-hidden={!showMetrics}>
              {METRICS.map((m) => (
                <button
                  key={m.key}
                  type="button"
                  className={`metric-btn ${selectedMetric === m.key ? 'active' : ''}`}
                  onClick={() => handleMetricClick(m.key)}
                >
                  {m.label}
                </button>
              ))}
            </section>
          </div>

          <button className="search-button" onClick={() => handleSearch()}>
            검색
          </button>
        </div>
      </section>

      <div className="data-lines card">
        {chartData && <Line data={chartData} />}
        {!chartData && errorMsg && <p className="data-empty">{errorMsg}</p>}
      </div>
    </div>
  );
}

export default CheckDataPage;
