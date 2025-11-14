import { useEffect } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import './App.css';
import { UniversitySelectionPage } from './pages/UniversitySelectionPage';
import { RoleSelectionPage } from './pages/RoleSelectionPage';
import { AbiturientDashboardPage } from './pages/abiturient/AbiturientDashboardPage';
import { UniversityInfoPage } from './pages/abiturient/sections/UniversityInfoPage';
import { ProgramsPage } from './pages/abiturient/sections/ProgramsPage';
import { AdmissionConditionsPage } from './pages/abiturient/sections/AdmissionConditionsPage';
import { OpenDayPage } from './pages/abiturient/sections/OpenDayPage';
import { AdmissionInquiryPage } from './pages/abiturient/sections/AdmissionInquiryPage';
import { StudentDashboardPage } from './pages/student/StudentDashboardPage';
import { TaskTrackerPage } from './pages/student/sections/TaskTrackerPage';
import { SchedulePage } from './pages/student/sections/SchedulePage';
import { VacanciesPage } from './pages/student/sections/VacanciesPage';
import { EventsPage } from './pages/student/sections/EventsPage';
import { CareerPage } from './pages/student/sections/CareerPage';
import { DeaneryPage } from './pages/student/sections/DeaneryPage';
import { DormitoryPage } from './pages/student/sections/DormitoryPage';
import { LibraryPage } from './pages/student/sections/LibraryPage';
import { ProjectsPage } from './pages/student/sections/ProjectsPage';
import { StaffDashboardPage } from './pages/staff/StaffDashboardPage';
import { StaffTravelPage } from './pages/staff/StaffTravelPage';
import { StaffVacationsPage } from './pages/staff/StaffVacationsPage';
import { StaffOfficePage } from './pages/staff/StaffOfficePage';
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { SettingsPage } from './pages/SettingsPage';
import { LoginPage } from './pages/LoginPage';
import { BottomNavBar } from './components/BottomNavBar';
import { useBottomNavContext } from './context/BottomNavContext';
import { fetchCurrentUser } from './api/auth';

function AppContent() {
  const location = useLocation();
  const { buttons } = useBottomNavContext();

  // Не показываем меню на страницах выбора
  const hideNav = location.pathname === '/' || location.pathname === '/university' || location.pathname === '/login';

  return (
    <>
      <Routes>
        <Route path="/" element={<RoleSelectionPage />} />
        <Route path="/university" element={<UniversitySelectionPage />} />
        <Route path="/dashboard/abiturient" element={<AbiturientDashboardPage />} />
        <Route path="/dashboard/abiturient/university-info" element={<UniversityInfoPage />} />
        <Route path="/dashboard/abiturient/programs" element={<ProgramsPage />} />
        <Route path="/dashboard/abiturient/admission-conditions" element={<AdmissionConditionsPage />} />
        <Route path="/dashboard/abiturient/open-day" element={<OpenDayPage />} />
        <Route path="/dashboard/abiturient/admission-inquiry" element={<AdmissionInquiryPage />} />
        <Route path="/dashboard/student" element={<StudentDashboardPage />} />
        <Route path="/dashboard/student/schedule" element={<SchedulePage />} />
        <Route path="/dashboard/student/vacancies" element={<VacanciesPage />} />
        <Route path="/dashboard/student/events" element={<EventsPage />} />
        <Route path="/dashboard/student/career" element={<CareerPage />} />
        <Route path="/dashboard/student/deanery" element={<DeaneryPage />} />
        <Route path="/dashboard/student/dormitory" element={<DormitoryPage />} />
        <Route path="/dashboard/student/library" element={<LibraryPage />} />
        <Route path="/dashboard/student/projects" element={<ProjectsPage />} />
        <Route path="/dashboard/student/task-tracker" element={<TaskTrackerPage />} />
        <Route path="/dashboard/staff" element={<StaffDashboardPage />} />
        <Route path="/dashboard/staff/travel" element={<StaffTravelPage />} />
        <Route path="/dashboard/staff/vacations" element={<StaffVacationsPage />} />
        <Route path="/dashboard/staff/office" element={<StaffOfficePage />} />
        <Route path="/dashboard/admin" element={<AdminDashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      {!hideNav && <BottomNavBar buttons={buttons} />}
    </>
  );
}

function App() {
  useEffect(() => {
    // При открытии приложения всегда вызываем auth/me
    fetchCurrentUser()
      .then((user) => {
        if (user) {
          console.log('Current user:', user);
        } else {
          console.log('User not authenticated');
        }
      })
      .catch((error) => {
        console.error('Failed to fetch current user:', error);
      });
  }, []);

  return <AppContent />;
}

export default App;
