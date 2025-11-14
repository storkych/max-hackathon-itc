import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

interface NavBarProps {
  title: string;
  backTo?: string;
  rightSlot?: ReactNode;
}

export function NavBar({ title, backTo, rightSlot }: NavBarProps) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (backTo) {
      navigate(backTo);
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="nav">
      <div className="nav-content">
        <button type="button" className="nav-back" onClick={handleBack} aria-label="Назад">
          ←
        </button>
        <div className="nav-title">{title}</div>
        <div style={{ minWidth: 40, display: 'flex', justifyContent: 'flex-end' }}>{rightSlot ?? <div style={{ width: 40 }} />}</div>
      </div>
    </div>
  );
}

