import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { useSession } from '../context/SessionContext';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();
  const { isLoggedIn, guardians, users, registerGuardian, registerUser, setSelectedUser } =
    useSession();

  const [uidInput, setUidInput] = useState('');
  const [showButtons, setShowButtons] = useState(false);

  const handleSearch = () => {
    const foundGuardian = guardians.find((g) => g.uid === uidInput);
    const foundUser = users.find((u) => u.uid === uidInput);

    if (foundGuardian) {
      navigate('/guardian');
    } else if (foundUser) {
      setSelectedUser(foundUser);
      navigate('/user');
    } else {
      setShowButtons(true);
    }
  };

  const handleRegisterGuardian = () => {
    registerGuardian(uidInput);
    setUidInput('');
    setShowButtons(false);
    navigate('/guardian');
  };

  const handleRegisterUser = () => {
    registerUser(uidInput);
    setUidInput('');
    setShowButtons(false);
    navigate('/user');
  };

  const goIfLoggedIn = (path) => {
    if (isLoggedIn) navigate(path);
    else alert('uid로 먼저 접속해주세요');
  };

  return (
    <div className="app-shell app-menu">
      <AppHeader />

      <div className="button-container">
        <button className="health" onClick={() => goIfLoggedIn('/health-feedback')}>
          <span className="btn-icon" aria-hidden="true">🤖</span>
          <span className="btn-label">사용자 맞춤 피드백</span>
        </button>

        <button className="feedback" onClick={() => goIfLoggedIn('/get-feedback')}>
          <span className="btn-icon" aria-hidden="true">📈</span>
          <span className="btn-label">데이터 확인</span>
        </button>

        <button className="medication" onClick={() => goIfLoggedIn('/medication')}>
          <span className="btn-icon" aria-hidden="true">💊</span>
          <span className="btn-label">복용 약 정보</span>
        </button>
      </div>

      {!isLoggedIn && (
        <div className="uid-search">
          <label className="uid-search-label">uid를 입력해주세요: </label>
          <input
            className="uid-search-input"
            type="text"
            value={uidInput}
            onChange={(e) => setUidInput(e.target.value)}
          />
          <button className="uid-search-button" onClick={handleSearch}>
            검색
          </button>
        </div>
      )}

      {showButtons && !isLoggedIn && (
        <div className="role-buttons">
          <button className="guardian-button" onClick={handleRegisterGuardian}>
            보호자
          </button>
          <button className="user-button" onClick={handleRegisterUser}>
            사용자
          </button>
        </div>
      )}
    </div>
  );
}

export default HomePage;
