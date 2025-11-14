import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../../components/DashboardLayout';
import type { DashboardSection } from '../../components/DashboardLayout';
import { useAppState } from '../../context/AppStateContext';
import { getIsFirstTime } from '../../api/settings';
import { fetchCurrentUser } from '../../api/auth';

interface CurrentUser {
  role?: string;
}

export function StudentDashboardPage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [userLoading, setUserLoading] = useState(true);

  useEffect(() => {
    if (!selectedUniversity) {
      navigate('/');
    }
  }, [navigate, selectedUniversity]);

  useEffect(() => {
    const checkFirstTime = async () => {
      const isFirstTime = await getIsFirstTime();
      console.log('[StudentDashboard] Page loaded, isFirstTime:', isFirstTime);
    };
    checkFirstTime();
  }, []);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const user = await fetchCurrentUser();
        setCurrentUser(user);
      } catch (error) {
        console.error('Failed to fetch current user', error);
        setCurrentUser(null);
      } finally {
        setUserLoading(false);
      }
    };
    loadUser();
  }, []);

  const isAuthenticated = Boolean(currentUser?.role && currentUser.role !== 'applicant');

  const publicSectionIds = ['schedule', 'task-tracker', 'events', 'vacancies'];

  const sections: DashboardSection[] = [
    {
      id: 'schedule',
      icon: 'schedule',
      title: 'Расписание',
      description: 'Персональное расписание занятий и расписание вашей группы.',
      route: '/dashboard/student/schedule',
    },
    {
      id: 'career',
      icon: 'career',
      title: 'Карьера и консультации',
      description: 'Записаться на карьерную консультацию и отслеживать статусы.',
      route: '/dashboard/student/career',
    },
    {
      id: 'vacancies',
      icon: 'vacancies',
      title: 'Вакансии партнеров',
      description: 'Подбор вакансий по интересующим направлениям и отклики.',
      route: '/dashboard/student/vacancies',
    },
    {
      id: 'deanery',
      icon: 'deanery',
      title: 'Деканат',
      description: 'Справки, оплата обучения, компенсации и академические отпуска.',
      route: '/dashboard/student/deanery',
    },
    {
      id: 'dormitory',
      icon: 'dormitory',
      title: 'Общежитие',
      description: 'Платежи, сервисы, гостевые пропуска и обращения в службу поддержки.',
      route: '/dashboard/student/dormitory',
    },
    {
      id: 'events',
      icon: 'events',
      title: 'События кампуса',
      description: 'Календарь событий и форма регистрации.',
      route: '/dashboard/student/events',
    },
    {
      id: 'library',
      icon: 'library',
      title: 'Библиотека',
      description: 'Каталог изданий, бронирование, электронные книги и оплату штрафов.',
      route: '/dashboard/student/library',
    },
    {
      id: 'projects',
      icon: 'projects',
      title: 'Проекты',
      description: 'Ваши команды и каталог проектных инициатив.',
      route: '/dashboard/student/projects',
    },
    {
      id: 'task-tracker',
      icon: 'task-tracker',
      title: 'Таск-трекер',
      description: 'Статусы задач по проектам и уведомления.',
      route: '/dashboard/student/task-tracker',
    },
  ];

  const filteredSections = sections.map((section) => {
    if (!isAuthenticated && !publicSectionIds.includes(section.id)) {
      return { ...section, hidden: true };
    }
    return section;
  });

  const authMessage = !userLoading && !isAuthenticated ? (
    <div className="card" style={{ marginTop: 24, background: 'var(--surface)', border: '1px solid var(--border-color)' }}>
      <div className="card-title">Для полного функционала необходима авторизация</div>
      <div className="card-description" style={{ marginTop: 8 }}>
        Войдите в аккаунт, чтобы получить доступ ко всем разделам: проекты, карьера, деканат, общежитие, библиотека и другим.
      </div>
      <button
        className="btn"
        type="button"
        onClick={() => navigate('/login')}
        style={{ marginTop: 16 }}
      >
        Войти в аккаунт
      </button>
    </div>
  ) : null;

  if (userLoading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="university-header">
            <div className="university-header-content">
              <div className="university-header-label">Ваш вуз</div>
              <div className="university-header-title">{selectedUniversity ?? 'Не выбран'}</div>
            </div>
          </div>

          <div className="menu-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="menu-item menu-item-skeleton">
                <div className="menu-icon menu-icon-skeleton"></div>
                <div className="menu-content" style={{ flex: 1 }}>
                  <div className="menu-title-skeleton"></div>
                  <div className="menu-description-skeleton"></div>
                </div>
                <span className="menu-arrow">→</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return <DashboardLayout sections={filteredSections} extraFooterContent={authMessage} />;
}

