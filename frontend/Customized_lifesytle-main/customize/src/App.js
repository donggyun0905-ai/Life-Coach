import { Routes, Route } from 'react-router-dom';

import BottomTabBar from './components/BottomTabBar';
import HomePage from './pages/HomePage';
import GuardianHome from './pages/GuardianHome';
import UserHome from './pages/UserHome';
import HealthFeedbackPage from './pages/HealthFeedbackPage';
import CheckDataPage from './pages/CheckDataPage';
import CheckfigPage from './pages/CheckfigPage';
import GetFeedbackPage from './pages/GetFeedbackPage';
import GuardianSharePage from './pages/GuardianSharePage';
import MedicationPage from './pages/MedicationPage';
import MediInfoPage from './pages/MediInfoPage';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/guardian" element={<GuardianHome />} />
        <Route path="/user" element={<UserHome />} />
        <Route path="/health-feedback" element={<HealthFeedbackPage />} />
        <Route path="/check-data" element={<CheckDataPage />} />
        <Route path="/check-fig" element={<CheckfigPage />} />
        <Route path="/get-feedback" element={<GetFeedbackPage />} />
        <Route path="/guardian-share" element={<GuardianSharePage />} />
        <Route path="/medication" element={<MedicationPage />} />
        <Route path="/medi-info" element={<MediInfoPage />} />
      </Routes>
      <BottomTabBar />
    </>
  );
}

export default App;
