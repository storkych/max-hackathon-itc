import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useAppState } from '../context/AppStateContext';
import { getAdmissionsUniversities, type AdmissionsUniversity } from '../api/admissions';
import { getIsFirstTime } from '../api/settings';

interface University extends AdmissionsUniversity {}

export function UniversitySelectionPage() {
  const navigate = useNavigate();
  const { setSelectedUniversity, selectedRole } = useAppState();
  const [searchTerm, setSearchTerm] = useState('');
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedRole) {
      navigate('/roles');
    }
  }, [navigate, selectedRole]);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getAdmissionsUniversities();
        if (mounted) {
          setUniversities(data as University[]);
        }
      } catch (loadError) {
        console.error('Failed to fetch universities', loadError);
        if (mounted) {
          setError('Не удалось загрузить список вузов. Попробуйте обновить страницу.');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredUniversities = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) {
      return universities;
    }
    return universities.filter((university) => university.name.toLowerCase().includes(term));
  }, [universities, searchTerm]);

  const handleSelectUniversity = async (university: University) => {
    setSelectedUniversity({ id: university.id, name: university.name });
    
    if (!selectedRole) {
      navigate('/roles');
      return;
    }

    // Для абитуриента - сразу на дашборд
    if (selectedRole === 'abiturient') {
      navigate('/dashboard/abiturient');
      return;
    }

    // Для студента - проверяем авторизацию и первый вход
    if (selectedRole === 'student') {
      const isFirstTime = await getIsFirstTime();
      console.log('[UniversitySelection] Student selected university, isFirstTime:', isFirstTime);
      // TODO: если первый раз - показать предложение войти с кнопкой "позже"
      navigate('/dashboard/student');
      return;
    }

    // Для сотрудника - обязательно вход
    if (selectedRole === 'staff') {
      navigate('/login');
      return;
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="text-center" style={{ marginTop: 40, marginBottom: 32 }}>
          <h2>Выберите ваш вуз</h2>
          <p className="subtitle">Для продолжения работы</p>
        </div>

        <div className="search-box">
          <span className="search-icon">
            <Search size={20} />
          </span>
          <input
            type="text"
            className="search-input"
            placeholder="Поиск вуза..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        {loading ? (
          <div className="university-list">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="university-item university-item-skeleton">
                <div className="university-name-skeleton">
                  <div className="university-name-line-skeleton"></div>
                  <div className="university-name-line-skeleton" style={{ width: '60%', marginTop: 8 }}></div>
                </div>
                <div className="university-arrow-skeleton"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="card">
            <div className="card-title">Ошибка</div>
            <div className="card-description">{error}</div>
          </div>
        ) : (
          <div className="university-list">
            {filteredUniversities.map((university) => (
              <button key={university.id} type="button" className="university-item" onClick={() => handleSelectUniversity(university)}>
                <span className="university-name">
                  {university.name}
                  <span style={{ display: 'block', fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                    {university.city} • {university.hasDormitory ? 'Общежитие есть' : 'Без общежития'}
                  </span>
                </span>
                <span className="university-arrow">→</span>
              </button>
            ))}
          </div>
        )}

        {!loading && !error && filteredUniversities.length === 0 ? (
          <div className="card mt-20">
            <div className="card-title">Ничего не найдено</div>
            <div className="card-description">Попробуйте изменить запрос или проверьте правильность написания</div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

