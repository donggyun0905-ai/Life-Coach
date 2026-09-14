import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { useSession } from '../context/SessionContext';
import { uploadPillImage } from '../api/pill';
import './MedicationPage.css';

function MedicationPage() {
  const navigate = useNavigate();
  const { selectedUser } = useSession();
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file) => {
    if (!file) return;

    const uid = selectedUser?.uid;
    if (!uid) {
      alert('UID가 없습니다.');
      return;
    }

    try {
      setUploading(true);
      const res = await uploadPillImage(uid, file);
      alert('알약 이미지 업로드 완료!');
      console.log('업로드 결과:', res);
    } catch (err) {
      console.error('업로드 실패:', err);
      alert('업로드 실패');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app-shell medication-container">
      <AppHeader />

      <button className="mediinfo" onClick={() => navigate('/medi-info')}>
        복용 약 정보 보기
      </button>

      <button className="takepill" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
        {uploading ? '업로드 중...' : '알약 찍기'}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={(e) => handleUpload(e.target.files[0])}
      />
    </div>
  );
}

export default MedicationPage;
