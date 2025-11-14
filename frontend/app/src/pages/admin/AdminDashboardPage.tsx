import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../../components/DashboardLayout';
import type { DashboardSection } from '../../components/DashboardLayout';
import { useAppState } from '../../context/AppStateContext';
import { getAdminDashboards, type AdminDashboard } from '../../api/admin';

export function AdminDashboardPage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  const [data, setData] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedUniversity) {
      navigate('/');
    }
  }, [navigate, selectedUniversity]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      try {
        const response = await getAdminDashboards();
        if (!mounted) {
          return;
        }
        setData(response);
      } catch (error) {
        console.error('Failed to load admin dashboard', error);
        if (mounted) {
          setData(null);
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

  const primaryMetrics = [
    { label: 'Студентов', value: data?.metrics?.students },
    { label: 'Сотрудников', value: data?.metrics?.staff },
    { label: 'Проектов', value: data?.metrics?.projects },
  ].filter((metric) => typeof metric.value === 'number');

  const academicMetrics = [
    { label: 'Средний GPA', value: data?.academicMetrics?.averageGrade },
    { label: 'Выпуск за год', value: data?.academicMetrics?.graduationRate ? `${data.academicMetrics.graduationRate}%` : undefined },
  ].filter((metric) => metric.value !== undefined);

  const sections: DashboardSection[] = [
    {
      id: 'campus-management',
      icon: 'campus-management',
      title: 'Ключевые показатели',
      description: 'Сводка по студентам, сотрудникам и проектам кампуса.',
      element: loading ? (
        <div className="card-description">Загрузка дашбордов...</div>
      ) : primaryMetrics.length === 0 ? (
        <div className="card-description">Нет данных о показателях кампуса.</div>
      ) : (
        <div className="stats-grid">
          {primaryMetrics.map((metric) => (
            <div key={metric.label} className="stat-card">
              <div className="stat-value">{metric.value?.toLocaleString('ru-RU')}</div>
              <div className="stat-label">{metric.label}</div>
            </div>
          ))}
        </div>
      ),
    },
    {
      id: 'academic-metrics',
      icon: 'academic-metrics',
      title: 'Академические показатели',
      description: 'Средний балл и показатели выпуска.',
      element: loading ? (
        <div className="card-description">Загрузка метрик...</div>
      ) : academicMetrics.length === 0 ? (
        <div className="card-description">Нет академических метрик.</div>
      ) : (
        <div className="card" style={{ marginBottom: 0 }}>
          <ul style={{ paddingLeft: 20, margin: 0 }}>
            {academicMetrics.map((metric) => (
              <li key={metric.label} style={{ marginBottom: 8 }}>
                <strong>{metric.label}:</strong> {metric.value}
              </li>
            ))}
          </ul>
        </div>
      ),
    },
    {
      id: 'news-aggregator',
      icon: 'news-aggregator',
      title: 'Новостной мониторинг',
      description: 'Последние упоминания кампуса в СМИ.',
      element: loading ? (
        <div className="card-description">Загрузка новостей...</div>
      ) : !data?.news || data.news.length === 0 ? (
        <div className="card-description">Свежих упоминаний нет.</div>
      ) : (
        <div style={{ display: 'grid', gap: 16 }}>
          {data.news.map((item) => (
            <div key={item.id} className="card" style={{ marginBottom: 0 }}>
              <div className="card-title">{item.title}</div>
              <div className="card-description">
                {item.source ?? 'Неизвестный источник'} •{' '}
                {item.publishedAt ? new Date(item.publishedAt).toLocaleDateString('ru-RU') : 'дата неизвестна'}
              </div>
            </div>
          ))}
        </div>
      ),
    },
  ];

  return <DashboardLayout sections={sections} />;
}

