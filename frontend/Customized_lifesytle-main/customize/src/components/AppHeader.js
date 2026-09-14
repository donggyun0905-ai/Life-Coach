import { useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import deepStreamImage from '../Deep_Stream.png';

// 모든 화면 상단에 고정으로 뜨는 로고 바 + 로그인 상태 표시.
// 예전엔 이 마크업이 컴포넌트 10곳에 그대로 복붙되어 있었다.
function AppHeader() {
  const navigate = useNavigate();
  const { isLoggedIn, selectedUser, logout } = useSession();

  const goHome = () => {
    if (!isLoggedIn) {
      navigate('/');
    } else if (selectedUser && selectedUser.uid) {
      navigate('/user');
    } else {
      navigate('/guardian');
    }
  };

  const handleLogout = () => {
    if (!isLoggedIn) return;
    logout();
    navigate('/');
  };

  return (
    <>
      <div className="image">
        <img
          className="deep-stream"
          src={deepStreamImage}
          alt="Deep stream"
          onClick={goHome}
        />
      </div>

      <div className="login-indicator">
        <button
          className={`login-dot ${isLoggedIn ? 'on' : 'off'}`}
          title={isLoggedIn ? '로그인됨 (클릭 시 로그아웃)' : '로그아웃 상태'}
          onClick={handleLogout}
        />
      </div>
    </>
  );
}

export default AppHeader;
