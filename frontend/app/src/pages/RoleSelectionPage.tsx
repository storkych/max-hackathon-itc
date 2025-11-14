import { useNavigate } from 'react-router-dom';
import { useAppState } from '../context/AppStateContext';
import type { UserRole } from '../context/AppStateContext';

const roles: Array<{
  id: UserRole;
  title: string;
  description: string;
  icon: string;
}> = [
  {
    id: 'abiturient',
    title: 'Абитуриент',
    description: 'Информация о поступлении, программах и условиях',
    icon: '🎓',
  },
  {
    id: 'student',
    title: 'Студент',
    description: 'Обучение, проекты, карьера и внеучебная деятельность',
    icon: '👨‍🎓',
  },
  {
    id: 'staff',
    title: 'Сотрудник вуза',
    description: 'Командировки, отпуска и офисные услуги',
    icon: '👔',
  },
];

export function RoleSelectionPage() {
  const navigate = useNavigate();
  const { setSelectedRole } = useAppState();

  const handleSelectRole = (role: (typeof roles)[number]) => {
    setSelectedRole(role.id);
    navigate('/university');
  };

  return (
    <div className="app-container" style={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
      <div className="container" style={{ width: '100%' }}>
        <div className="text-center" style={{ marginBottom: 32 }}>
          <h1>Добро пожаловать!</h1>
          <p className="subtitle">Выберите вашу роль для продолжения</p>
        </div>

        <div className="role-grid">
          {roles.map((role) => (
            <button key={role.id} type="button" className="role-card" onClick={() => handleSelectRole(role)}>
              <div className="role-icon">{role.icon}</div>
              <div className="role-title">{role.title}</div>
              <div className="role-description">{role.description}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

