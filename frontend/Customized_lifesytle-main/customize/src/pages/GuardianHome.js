import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { useSession } from '../context/SessionContext';
import './GuardianHome.css';

function GuardianHome() {
  const navigate = useNavigate();
  const { users, selectedUser, upsertUser, setSelectedUser } = useSession();

  const [showRegister, setShowRegister] = useState(false);
  const [userUid, setUserUid] = useState('');
  const [userNickname, setUserNickname] = useState('');
  const [showList, setShowList] = useState(false);

  const handleSaveUser = () => {
    if (!userUid || !userNickname) return;
    const isExisting = users.some((u) => u.uid === userUid);
    upsertUser(userUid, userNickname);
    alert(isExisting ? '기존 사용자 UID의 별명을 수정했습니다!' : '새 사용자 등록 완료!');
    setUserUid('');
    setUserNickname('');
    setShowRegister(false);
  };

  // 보호자 화면에서는 사용자가 선택돼 있어야 하위 화면으로 이동 가능
  const navigateWithUser = (path) => {
    if (selectedUser && selectedUser.uid) navigate(path);
  };

  const handleSwitchToUser = () => {
    if (selectedUser && selectedUser.uid) {
      navigate('/user');
      return;
    }
    if (users.length === 1) {
      setSelectedUser(users[0]);
      navigate('/user');
      return;
    }
    alert('전환하려면 먼저 사용자를 선택하거나 등록하세요.');
  };

  return (
    <div className="app-shell">
      <AppHeader />

      <h3 className="guardian-title">보호자 화면</h3>

      <div className="button-container">
        <button className="guardian-health" onClick={() => navigateWithUser('/health-feedback')}>
          <span className="btn-icon" aria-hidden="true">🤖</span>
          <span className="btn-label">사용자 맞춤 피드백</span>
        </button>

        <button className="guardian-feedback" onClick={() => navigateWithUser('/get-feedback')}>
          <span className="btn-icon" aria-hidden="true">📈</span>
          <span className="btn-label">데이터 확인</span>
        </button>

        <button className="guardian-medication" onClick={() => navigateWithUser('/medication')}>
          <span className="btn-icon" aria-hidden="true">💊</span>
          <span className="btn-label">복용 약 정보</span>
        </button>

        <button className="register" onClick={() => setShowRegister(true)}>
          <span className="btn-icon" aria-hidden="true">👤</span>
          <span className="btn-label">사용자 등록</span>
        </button>
      </div>

      <div className="conversion">
        <button className="toggle-view" onClick={handleSwitchToUser}>
          🔁 전환
        </button>
      </div>

      {showRegister && (
        <div className="guardian-input">
          <label className="guardian-label-user">사용자 UID: </label>
          <input
            className="guardian-input-field"
            type="text"
            value={userUid}
            onChange={(e) => setUserUid(e.target.value)}
          />
          <label className="guardian-label-nick">별명: </label>
          <input
            className="guardian-input-field"
            type="text"
            value={userNickname}
            onChange={(e) => setUserNickname(e.target.value)}
          />
          <button className="guardian-save" onClick={handleSaveUser}>
            저장
          </button>
        </div>
      )}

      <div className="user-list-toggle">
        <button className="user" onClick={() => setShowList((s) => !s)}>
          📋 사용자 목록
        </button>
      </div>

      {showList && (
        <div className="user-list">
          <h4>등록된 사용자</h4>
          <ul>
            {users.map((u, index) => (
              <li key={index}>
                <button
                  className="user-name"
                  onClick={() => {
                    setSelectedUser(u);
                    navigate('/user');
                  }}
                >
                  {u.nickname}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default GuardianHome;
