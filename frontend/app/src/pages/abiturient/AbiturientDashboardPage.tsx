import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../../components/DashboardLayout';
import type { DashboardSection } from '../../components/DashboardLayout';
import { useAppState } from '../../context/AppStateContext';

export function AbiturientDashboardPage() {
  const { selectedUniversityId } = useAppState();
  const navigate = useNavigate();

  useEffect(() => {
    if (!selectedUniversityId) {
      navigate('/');
    }
  }, [navigate, selectedUniversityId]);

  const sections: DashboardSection[] = [
    {
      id: 'university-info',
      icon: 'university-info',
      title: 'Информация о вузе',
      description: 'История, направления подготовки и преимущества выбранного вуза.',
      route: '/dashboard/abiturient/university-info',
    },
    {
      id: 'programs',
      icon: 'programs',
      title: 'Образовательные программы',
      description: 'Список программ, их формат обучения, сроки и особенности.',
      route: '/dashboard/abiturient/programs',
    },
    {
      id: 'admission-conditions',
      icon: 'admission-conditions',
      title: 'Условия поступления',
      description: 'Минимальные баллы, индивидуальные достижения и список документов.',
      route: '/dashboard/abiturient/admission-conditions',
    },
    {
      id: 'open-day',
      icon: 'open-day',
      title: 'Дни открытых дверей',
      description: 'Ближайшие мероприятия и форма регистрации. Поддерживается идемпотентность запросов.',
      route: '/dashboard/abiturient/open-day',
    },
    {
      id: 'admission-inquiry',
      icon: 'admission-inquiry',
      title: 'Вопрос в приёмную комиссию',
      description: 'Форма обращения с поддержкой вложений. Идемпотентность обеспечивается по ключу запроса.',
      route: '/dashboard/abiturient/admission-inquiry',
    },
  ];

  return (
    <DashboardLayout
      sections={sections}
    />
  );
}

