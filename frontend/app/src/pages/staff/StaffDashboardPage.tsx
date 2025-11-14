import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../../components/DashboardLayout';
import type { DashboardSection } from '../../components/DashboardLayout';
import { useAppState } from '../../context/AppStateContext';

export function StaffDashboardPage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  useEffect(() => {
    if (!selectedUniversity) {
      navigate('/');
    }
  }, [selectedUniversity, navigate]);

  const sections: DashboardSection[] = [
    {
      id: 'business-trips',
      icon: 'business-trips',
      title: 'Командировки',
      description: 'Создание запросов и отслеживание статусов командировок.',
      route: '/dashboard/staff/travel',
    },
    {
      id: 'vacations',
      icon: 'vacations',
      title: 'Отпуска',
      description: 'Планирование отпусков и отправка заявок на согласование.',
      route: '/dashboard/staff/vacations',
    },
    {
      id: 'office',
      icon: 'office',
      title: 'Офис и HR',
      description: 'Гостевые пропуска и взаимодействие с офисом.',
      route: '/dashboard/staff/office',
    },
  ];

  return <DashboardLayout sections={sections} />;
}


