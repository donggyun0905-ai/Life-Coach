import { useEffect, useState } from 'react';
import AppHeader from '../components/AppHeader';
import CloseButton from '../components/CloseButton';
import { useSession } from '../context/SessionContext';
import { getPillList, deletePill } from '../api/pill';
import './MediInfoPage.css';

function MediInfoPage() {
  const { selectedUser } = useSession();
  const uid = selectedUser?.uid;

  const [meds, setMeds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadList = async () => {
    if (!uid) {
      setError('UID가 없습니다.');
      setMeds([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getPillList(uid);
      setMeds(data || []);
    } catch (err) {
      console.error('복용 약 정보 불러오기 실패:', err);
      setError('복용 약 정보를 불러오지 못했습니다.');
      setMeds([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid]);

  const handleDelete = async (id) => {
    if (!window.confirm('이 약 정보를 삭제하시겠습니까?')) return;

    try {
      await deletePill(id);
      await loadList();
    } catch (err) {
      console.error('삭제 실패:', err);
      alert('삭제에 실패했습니다.');
    }
  };

  return (
    <div className="app-shell mediinfo-container">
      <AppHeader />
      <CloseButton to="/medication" />

      <div className="mediInfo">
        {loading ? (
          <div className="mediinfo-text">복용 약 정보를 불러오는 중...</div>
        ) : error ? (
          <div className="mediinfo-text">{error}</div>
        ) : !meds || meds.length === 0 ? (
          <div className="mediinfo-text">약의 정보가 없습니다.</div>
        ) : (
          <div className="medi-list">
            <table>
              <thead>
                <tr>
                  <th>약 이름</th>
                  <th>약 정보</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {meds.map((m, idx) => (
                  <tr key={m.id ?? idx}>
                    <td className="medi-name">{m.pill_name ?? `약 ${idx + 1}`}</td>

                    <td className="medi-info">
                      {m.main_usage && <div className="pill-main-usage">효능: {m.main_usage}</div>}
                      {m.warning && <div className="pill-warning">주의: {m.warning}</div>}
                    </td>

                    <td>
                      <button className="medi-delete" type="button" onClick={() => handleDelete(m.id)}>
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default MediInfoPage;
