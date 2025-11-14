import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { getIcon } from './Icons';
import { useAppState } from '../context/AppStateContext';

export interface DashboardSection {
  id: string;
  icon?: string;
  title: string;
  description?: string;
  route?: string;
  element?: ReactNode;
  hidden?: boolean;
}

interface DashboardLayoutProps {
  sections: DashboardSection[];
  extraHeaderContent?: ReactNode;
  extraFooterContent?: ReactNode;
}

export function DashboardLayout({
  sections,
  extraHeaderContent,
  extraFooterContent,
}: DashboardLayoutProps) {
  const navigate = useNavigate();
  const { selectedUniversity } = useAppState();

  const visibleSections = sections.filter((section) => !section.hidden);

  const handleSectionClick = (section: DashboardSection) => {
    if (section.route) {
      navigate(section.route);
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        {/* Блок с названием вуза */}
        <div className="university-header">
          <div className="university-header-content">
            <div className="university-header-label">Ваш вуз</div>
            <div className="university-header-title">{selectedUniversity ?? 'Не выбран'}</div>
          </div>
        </div>

        {extraHeaderContent}

        <div className="menu-grid">
          {visibleSections.map((section) => {
            const iconElement = section.icon ? getIcon(section.icon) : null;
            return (
              <button
                key={section.id}
                className="menu-item"
                onClick={() => handleSectionClick(section)}
                type="button"
              >
                {iconElement ? (
                  <div className="menu-icon" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {iconElement}
                  </div>
                ) : null}
                <div className="menu-content">
                  <div className="menu-title">{section.title}</div>
                  {section.description ? <div className="menu-description">{section.description}</div> : null}
                </div>
                <span className="menu-arrow">→</span>
              </button>
            );
          })}
        </div>

        {extraFooterContent}
      </div>
    </div>
  );
}

