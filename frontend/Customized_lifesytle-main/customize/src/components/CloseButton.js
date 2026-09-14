import { useNavigate } from 'react-router-dom';

// 화면 우상단에 고정으로 뜨는 "닫기" 버튼. 기본 동작은 브라우저 뒤로가기와 동일하게
// 이전 화면으로 돌아간다 (React Router 히스토리 사용).
function CloseButton({ to, label = '닫기' }) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (to) navigate(to);
    else navigate(-1);
  };

  return (
    <button className="top-close-btn" onClick={handleClick}>
      {label}
    </button>
  );
}

export default CloseButton;
