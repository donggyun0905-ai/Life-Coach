import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import './HealthFeedbackPage.css';

function HealthFeedbackPage() {
  const navigate = useNavigate();

  return (
    <div className="app-shell healthfeedback-container">
      <AppHeader />
      <CloseButton />

      <h1 className="hf-title">저장된 건강 데이터</h1>

      <div className="hf-buttons">
        <button className="button-data" onClick={() => navigate('/check-data')}>
          <div className="hf-content">
            <span className="hf-icon" aria-hidden="true">💾</span>
            <span className="hf-label">저장된 데이터<br />확인</span>
          </div>
        </button>

        <button className="button-feedback" onClick={() => navigate('/check-fig')}>
          <div className="hf-content">
            <span className="hf-icon" aria-hidden="true">📊</span>
            <span className="hf-label">저장된 데이터<br />기반 피드백</span>
          </div>
        </button>
      </div>
    </div>
  );
}

export default HealthFeedbackPage;
