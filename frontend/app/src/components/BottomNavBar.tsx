import { useNavigate, useLocation } from 'react-router-dom';
import { useAppState } from '../context/AppStateContext';
import { getIcon } from './Icons';
import type { BottomNavButton } from '../api/settings';
import './BottomNavBar.css';

interface BottomNavBarProps {
  buttons: BottomNavButton[];
}

function getDashboardRoute(role: string): string {
  switch (role) {
    case 'abiturient':
      return '/dashboard/abiturient';
    case 'student':
      return '/dashboard/student';
    case 'staff':
      return '/dashboard/staff';
    case 'admin':
      return '/dashboard/admin';
    default:
      return '/';
  }
}

function getDashboardIcon(): string {
  // Для всех ролей используем Home для главной страницы
  return 'home';
}

export function BottomNavBar({ buttons }: BottomNavBarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedRole } = useAppState();

  if (!selectedRole) {
    return null;
  }

  const dashboardRoute = getDashboardRoute(selectedRole);
  const dashboardIcon = getDashboardIcon();
  const settingsRoute = '/settings';
  
  // Ограничиваем до 3 кнопок между Главная и Настройки
  const middleButtons = buttons.filter((b) => b.id !== 'dashboard' && b.id !== 'settings').slice(0, 3);
  
  // Определяем активность для Главной (только на главной странице дашборда, не на подстраницах)
  const isDashboardActive = location.pathname === dashboardRoute;
  
  // Определяем активность для Настроек
  const isSettingsActive = location.pathname === settingsRoute;

  const buttonColor = buttons[0]?.color || '#0077FF';
  const buttonStyle = { '--button-color': buttonColor } as React.CSSProperties;

  return (
    <nav className="bottom-nav">
      {/* Фиксированная кнопка "Главная" слева */}
      <button
        type="button"
        className={`bottom-nav-button ${isDashboardActive ? 'active' : ''}`}
        onClick={() => navigate(dashboardRoute)}
        style={buttonStyle}
      >
        <div className="bottom-nav-icon">{getIcon(dashboardIcon)}</div>
        <span className="bottom-nav-label">Главная</span>
      </button>

      {/* Выбранные пользователем кнопки (0-3) */}
      {middleButtons.map((button) => {
        const isActive = location.pathname === button.route || location.pathname.startsWith(button.route + '/');
        const iconElement = button.icon ? getIcon(button.icon) : null;

        return (
          <button
            key={button.id}
            type="button"
            className={`bottom-nav-button ${isActive ? 'active' : ''}`}
            onClick={() => navigate(button.route)}
            style={buttonStyle}
          >
            {iconElement ? <div className="bottom-nav-icon">{iconElement}</div> : null}
            <span className="bottom-nav-label">{button.label}</span>
          </button>
        );
      })}

      {/* Фиксированная кнопка "Настройки" справа */}
      <button
        type="button"
        className={`bottom-nav-button ${isSettingsActive ? 'active' : ''}`}
        onClick={() => navigate(settingsRoute)}
        style={buttonStyle}
      >
        <div className="bottom-nav-icon">{getIcon('office')}</div>
        <span className="bottom-nav-label">Настройки</span>
      </button>
    </nav>
  );
}

