import { useEffect, useState } from 'react';
import { MapPin, Globe, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../../context/AppStateContext';
import { getAdmissionsUniversityById } from '../../../api/admissions';

const FEATURE_LABELS: Record<string, string> = {
  has_distance_programs: 'Дистанционные программы',
  has_dormitory: 'Общежитие',
  has_military_department: 'Военная кафедра',
  has_open_day: 'Дни открытых дверей',
  has_preparatory_courses: 'Подготовительные курсы',
};

const FALLBACK_CAMPUS_IMAGE =
  'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300"><rect width="800" height="300" fill="%23f0f2f5"/><path d="M0 220h800v80H0z" fill="%23dee3ea"/><path d="M80 200h120v100H80zM240 170h140v130H240zM420 190h110v110H420zM560 160h160v140H560z" fill="%23cbd3df"/><path d="M260 150l50-60 50 60z" fill="%23aab6c6"/><path d="M600 130l80-90 80 90z" fill="%23909fb4"/><circle cx="130" cy="150" r="40" fill="%23d7dde7"/></svg>';

const FALLBACK_LOGO_IMAGE =
  'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" rx="32" ry="32" fill="%23f0f2f5"/><circle cx="100" cy="80" r="36" fill="%23cbd3df"/><path d="M50 160c12-24 40-40 50-40s38 16 50 40" stroke="%23909fb4" stroke-width="10" fill="none" stroke-linecap="round"/></svg>';

function withFallback(src: string | undefined | null, fallback: string) {
  if (!src) {
    return fallback;
  }
  if (src.includes('example.com')) {
    return fallback;
  }
  return src;
}

export function UniversityInfoPage() {
  const { selectedUniversityId } = useAppState();
  const navigate = useNavigate();
  const [universityInfo, setUniversityInfo] = useState<Awaited<ReturnType<typeof getAdmissionsUniversityById>>>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedUniversityId) {
      navigate('/');
      return;
    }

    let mounted = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const university = await getAdmissionsUniversityById(selectedUniversityId);
        if (mounted) {
          setUniversityInfo(university);
        }
      } catch (loadError) {
        console.error('Failed to load university info', loadError);
        if (mounted) {
          setError('Не удалось загрузить информацию о вузе.');
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
  }, [selectedUniversityId, navigate]);

  if (loading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card">
            <div className="skeleton-line" style={{ width: '40%' }} />
            <div className="skeleton-line" style={{ width: '70%' }} />
            <div className="skeleton-line" style={{ width: '60%' }} />
          </div>
        </div>
      </div>
    );
  }

  if (error || !universityInfo) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card">
            <div className="card-title">Ошибка</div>
            <div className="card-description">{error ?? 'Данные недоступны. Попробуйте выбрать другой вуз.'}</div>
          </div>
        </div>
      </div>
    );
  }

  const features = Object.entries(FEATURE_LABELS)
    .filter(([key]) => universityInfo.features?.[key as keyof typeof universityInfo.features])
    .map(([, label]) => label);

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>{universityInfo.title ?? universityInfo.shortTitle ?? universityInfo.name}</h1>
            <p className="subtitle">{universityInfo.about ?? universityInfo.description}</p>
          </div>
        </div>

        <div className="university-grid">
          <div className="card university-hero">
            <img
              src={withFallback(universityInfo.media?.imageUrl, FALLBACK_CAMPUS_IMAGE)}
              alt={universityInfo.title ?? universityInfo.name}
              className="university-hero-image"
            />
            <div className="university-hero-body">
              <div className="university-heading">
                <img src={withFallback(universityInfo.media?.logoUrl, FALLBACK_LOGO_IMAGE)} alt="Логотип" className="university-logo" />
                <div>
                  <h2>{universityInfo.shortTitle ?? universityInfo.title ?? universityInfo.name}</h2>
                  <div className="university-meta">
                    <span>
                      <MapPin size={16} />
                      {universityInfo.city ?? universityInfo.region ?? 'Город уточняется'}
                    </span>
                    <span>Обновлено: {new Date(universityInfo.lastUpdated ?? universityInfo.meta?.last_updated ?? Date.now()).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>
              </div>
              <p>{universityInfo.description}</p>

              <div className="university-stats">
                <div className="university-stat">
                  <div className="university-stat-label">Студентов</div>
                  <div className="university-stat-value">
                    {(universityInfo.stats?.studentsTotal ?? 0).toLocaleString('ru-RU')} +
                  </div>
                </div>
                <div className="university-stat">
                  <div className="university-stat-label">Программ</div>
                  <div className="university-stat-value">{universityInfo.stats?.programsCount ?? '—'}</div>
                </div>
                <div className="university-stat">
                  <div className="university-stat-label">Трудоустройство</div>
                  <div className="university-stat-value">
                    {universityInfo.stats?.employmentRate ? `${universityInfo.stats.employmentRate}%` : '—'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="card university-contacts">
            <div className="card-title">Контакты</div>
            <div className="contact-row">
              <span>Адрес</span>
              <span>{universityInfo.contacts?.address ?? 'Информация уточняется'}</span>
            </div>
            <div className="contact-row">
              <span>Телефон</span>
              <span>{universityInfo.contacts?.phone ?? 'Информация уточняется'}</span>
            </div>
            <div className="contact-row">
              <span>Email</span>
              <span>{universityInfo.contacts?.email ?? 'Информация уточняется'}</span>
            </div>
            <div className="contact-row">
              <span>Сайт</span>
              {universityInfo.contacts?.site ? (
                <a href={universityInfo.contacts.site} target="_blank" rel="noreferrer">
                  <Globe size={14} />
                  {universityInfo.contacts.site.replace(/^https?:\/\//, '')}
                </a>
              ) : (
                <span>Информация уточняется</span>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-title">Особенности</div>
            {features.length === 0 ? (
              <div className="card-description">Информация уточняется.</div>
            ) : (
              <div className="university-feature-grid">
                {features.map((feature) => (
                  <span key={feature} className="university-feature">
                    <CheckCircle size={14} />
                    {feature}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

