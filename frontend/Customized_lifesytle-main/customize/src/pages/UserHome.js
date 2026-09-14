import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { useSession } from '../context/SessionContext';
import './UserHome.css';

function UserHome() {
  const navigate = useNavigate();
  const { selectedUser } = useSession();

  const requireUserThenNavigate = (path) => {
    if (!selectedUser || !selectedUser.uid) {
      alert('사용자가 선택되지 않았습니다.');
      return;
    }
    navigate(path);
  };

  return (
    <div className="app-shell">
      <AppHeader />

      <h3 className="user-title">사용자 화면</h3>
      <p className="now-user">
        현재 사용자: {selectedUser?.nickname} ({selectedUser?.uid})
      </p>

      <div className="button-container">
        <button className="user-health" onClick={() => requireUserThenNavigate('/health-feedback')}>
          <span className="btn-icon" aria-hidden="true">🤖</span>
          <span className="btn-label">사용자 맞춤 피드백</span>
        </button>
        <button className="user-feedback" onClick={() => requireUserThenNavigate('/get-feedback')}>
          <span className="btn-icon" aria-hidden="true">📈</span>
          <span className="btn-label">데이터 확인</span>
        </button>
        <button className="user-medication" onClick={() => requireUserThenNavigate('/medication')}>
          <span className="btn-icon" aria-hidden="true">💊</span>
          <span className="btn-label">복용 약 정보</span>
        </button>
      </div>

      <div className="conversion">
        <button className="toggle-view" onClick={() => navigate('/guardian')}>
          🔁 전환
        </button>
      </div>
    </div>
  );
}

export default UserHome;
