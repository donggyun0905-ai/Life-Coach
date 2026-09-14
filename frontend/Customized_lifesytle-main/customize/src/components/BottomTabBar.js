import { useLocation, useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';

// 로그인 후 모든 화면 하단에 고정으로 뜨는 탭바.
// 어느 화면에 있든 3개 핵심 영역을 한 번의 탭으로 즉시 전환할 수 있게 한다.
const TABS = [
  { key: 'feedback', icon: '🤖', label: '피드백', path: '/health-feedback', match: ['/health-feedback', '/check-data', '/check-fig'] },
  { key: 'data', icon: '📈', label: '데이터', path: '/get-feedback', match: ['/get-feedback', '/guardian-share'] },
  { key: 'medication', icon: '💊', label: '복약', path: '/medication', match: ['/medication', '/medi-info'] },
];

function BottomTabBar() {
  const { isLoggedIn } = useSession();
  const location = useLocation();
  const navigate = useNavigate();

  if (!isLoggedIn) return null;

  return (
    <nav className="bottom-tab-bar">
      {TABS.map((tab) => {
        const active = tab.match.includes(location.pathname);
        return (
          <button
            key={tab.key}
            className={`tab-btn ${active ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
            aria-current={active ? 'page' : undefined}
          >
            <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

export default BottomTabBar;
