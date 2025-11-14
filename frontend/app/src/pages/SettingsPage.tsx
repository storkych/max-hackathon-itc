import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../context/AppStateContext';
import { useBottomNavContext } from '../context/BottomNavContext';
import type { BottomNavButton } from '../api/settings';
import { getAvailableBottomNavButtons } from '../utils/bottomNavConfig';
import { getIcon } from '../components/Icons';
import { fetchCurrentUser, logout, type CurrentUser } from '../api/auth';
import { Pencil } from 'lucide-react';
import './SettingsPage.css';

export function SettingsPage() {
  const navigate = useNavigate();
  const { selectedRole, selectedUniversity } = useAppState();
  const { buttons: currentButtons, updateButtons, refresh } = useBottomNavContext();
  const [selectedButtons, setSelectedButtons] = useState<(BottomNavButton | null)[]>([null, null, null]);
  const [saving, setSaving] = useState(false);
  const [draggedItem, setDraggedItem] = useState<{ type: 'selected' | 'available'; index: number; button: BottomNavButton } | null>(null);
  const [dragOverSlot, setDragOverSlot] = useState<number | null>(null);
  const [touchStartPos, setTouchStartPos] = useState<{ x: number; y: number } | null>(null);
  const [dragPosition, setDragPosition] = useState<{ x: number; y: number } | null>(null);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [userLoading, setUserLoading] = useState(true);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [lastSavedButtons, setLastSavedButtons] = useState<string>('');

  useEffect(() => {
    if (!selectedRole) {
      navigate('/');
      return;
    }

    // Фильтруем "Главная" и "Настройки" из текущих кнопок
    const filteredButtons = currentButtons.filter((b) => b.id !== 'dashboard' && b.id !== 'settings');
    
    // Заполняем слоты сохраненными кнопками, если они есть
    const slots: (BottomNavButton | null)[] = [null, null, null];
    filteredButtons.slice(0, 3).forEach((btn, idx) => {
      slots[idx] = btn;
    });
    setSelectedButtons(slots);
    setIsInitialLoad(true);
    // Сохраняем строковое представление для сравнения
    const buttonsString = JSON.stringify(slots.filter((b) => b !== null).map((b) => ({ id: b?.id, route: b?.route })));
    setLastSavedButtons(buttonsString);
  }, [currentButtons, selectedRole, navigate]);

  // Автоматическое сохранение при изменении кнопок
  useEffect(() => {
    if (isInitialLoad || !selectedRole) {
      setIsInitialLoad(false);
      return;
    }

    // Сравниваем текущее состояние с последним сохраненным
    const currentButtonsString = JSON.stringify(
      selectedButtons.filter((b) => b !== null).map((b) => ({ id: b?.id, route: b?.route }))
    );

    // Если ничего не изменилось, не сохраняем
    if (currentButtonsString === lastSavedButtons) {
      return;
    }

    const saveTimeout = setTimeout(async () => {
      setSaving(true);
      try {
        const buttonsWithColor = selectedButtons
          .filter((btn): btn is BottomNavButton => btn !== null)
          .map((btn) => ({
            ...btn,
            color: btn.color || '#0077FF',
          }));
        await updateButtons(buttonsWithColor);
        // Обновляем последнее сохраненное состояние
        setLastSavedButtons(currentButtonsString);
      } catch (error) {
        console.error('Failed to save settings', error);
      } finally {
        setSaving(false);
      }
    }, 500); // Задержка 500ms для debounce

    return () => clearTimeout(saveTimeout);
  }, [selectedButtons, selectedRole, isInitialLoad, lastSavedButtons, updateButtons]);

  useEffect(() => {
    const loadUser = async () => {
      setUserLoading(true);
      try {
        const user = await fetchCurrentUser();
        setCurrentUser(user);
      } catch (error) {
        console.error('Failed to fetch user', error);
        setCurrentUser(null);
      } finally {
        setUserLoading(false);
      }
    };

    loadUser();
  }, []);

  // Определяем доступные кнопки в зависимости от роли и авторизации
  const availableButtons = useMemo(() => {
    if (!selectedRole) return [];
    const isStudentAuthenticated =
      selectedRole === 'student' ? Boolean(currentUser?.role && currentUser.role !== 'applicant') : undefined;
    return getAvailableBottomNavButtons(selectedRole, { isStudentAuthenticated });
  }, [selectedRole, currentUser]);

  // Визуальный элемент-призрак для перетаскивания (для всех типов перетаскивания)
  const dragGhost = draggedItem && dragPosition ? (
    <div
      className="settings-drag-ghost"
      style={{
        position: 'fixed',
        left: dragPosition.x,
        top: dragPosition.y,
        pointerEvents: 'none',
        zIndex: 10000,
        transform: 'translate(-50%, -50%)',
      }}
    >
      {draggedItem.button.icon ? (
        <div className="settings-button-icon-small">{getIcon(draggedItem.button.icon)}</div>
      ) : null}
      <span className="settings-button-label-small">{draggedItem.button.label}</span>
    </div>
  ) : null;

  // Убрана возможность перетаскивания из слотов

  const handleAvailableDragStart = (e: React.DragEvent, button: BottomNavButton) => {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/html', '');
    setDragPosition({ x: e.clientX, y: e.clientY });
    setDraggedItem({ type: 'available', index: -1, button });
    document.body.style.overflow = 'hidden';
  };
  
  // Отслеживаем движение мыши для drag событий
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggedItem) {
        setDragPosition({ x: e.clientX, y: e.clientY });
      }
    };

    if (draggedItem) {
      document.addEventListener('mousemove', handleMouseMove);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
      };
    }
  }, [draggedItem]);

  // Touch события для мобильных устройств
  // Не используем preventDefault, так как CSS touch-action: none уже предотвращает прокрутку
  // Убрана возможность перетаскивания из слотов

  const handleAvailableTouchStart = (e: React.TouchEvent, button: BottomNavButton) => {
    const touch = e.touches[0];
    setTouchStartPos({ x: touch.clientX, y: touch.clientY });
    setDragPosition({ x: touch.clientX, y: touch.clientY });
    setDraggedItem({ type: 'available', index: -1, button });
    document.body.style.overflow = 'hidden';
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!draggedItem || !touchStartPos) return;
    
    const touch = e.touches[0];
    const deltaX = Math.abs(touch.clientX - touchStartPos.x);
    const deltaY = Math.abs(touch.clientY - touchStartPos.y);
    
    // Обновляем позицию перетаскиваемого элемента для всех типов
    setDragPosition({ x: touch.clientX, y: touch.clientY });
    
    // Если движение достаточно большое, считаем это перетаскиванием
    if (deltaX > 10 || deltaY > 10) {
      // Не используем preventDefault, так как CSS touch-action: none уже предотвращает прокрутку
      
      // Находим слот под пальцем, проверяя координаты всех слотов
      // Перетаскивание из слотов отключено, обрабатываем только перетаскивание из доступных кнопок
      if (draggedItem.type === 'available') {
        const slotsContainer = document.querySelector('.settings-slots-container');
        if (slotsContainer) {
          const allSlots = Array.from(slotsContainer.children) as HTMLElement[];
          for (let i = 0; i < allSlots.length && i < 3; i++) {
            const slot = allSlots[i];
            const rect = slot.getBoundingClientRect();
            if (touch.clientX >= rect.left && touch.clientX <= rect.right &&
                touch.clientY >= rect.top && touch.clientY <= rect.bottom) {
              setDragOverSlot(i);
              break;
            }
          }
        }
      }
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!draggedItem || !touchStartPos) {
      setTouchStartPos(null);
      setDraggedItem(null);
      setDragOverSlot(null);
      setDragPosition(null);
      document.body.style.overflow = '';
      return;
    }

    // Не используем preventDefault, так как CSS touch-action: none уже предотвращает прокрутку

    const touch = e.changedTouches[0];
    
    // Определяем целевой слот, проверяя координаты всех слотов
    let targetSlot: number | null = null;
    const slotsContainer = document.querySelector('.settings-slots-container');
    if (slotsContainer) {
      const allSlots = Array.from(slotsContainer.children) as HTMLElement[];
      for (let i = 0; i < allSlots.length && i < 3; i++) {
        const slot = allSlots[i];
        const rect = slot.getBoundingClientRect();
        if (touch.clientX >= rect.left && touch.clientX <= rect.right &&
            touch.clientY >= rect.top && touch.clientY <= rect.bottom) {
          targetSlot = i;
          break;
        }
      }
    }
    
    // Используем dragOverSlot если он установлен, иначе пытаемся определить из позиции
    const finalSlot = dragOverSlot !== null ? dragOverSlot : targetSlot;
    
    // Перетаскивание из слотов отключено, обрабатываем только перетаскивание из доступных кнопок
    if (finalSlot !== null && draggedItem.type === 'available') {
      // Для перетаскивания из доступных кнопок
      setSelectedButtons((prev) => {
        const newSlots = [...prev];
        const existingIndex = newSlots.findIndex((btn) => btn?.id === draggedItem.button.id);
        
        if (existingIndex !== -1) {
          [newSlots[existingIndex], newSlots[finalSlot]] = [newSlots[finalSlot], newSlots[existingIndex]];
        } else {
          newSlots[finalSlot] = {
            ...draggedItem.button,
            color: '#0077FF',
          };
        }
        
        return newSlots;
      });
    }

    setTouchStartPos(null);
    setDraggedItem(null);
    setDragOverSlot(null);
    setDragPosition(null);
    document.body.style.overflow = '';
  };

  const handleSlotDragOver = (e: React.DragEvent, slotIndex: number) => {
    e.preventDefault();
    e.stopPropagation();
    // Перетаскивание из слотов отключено, обрабатываем только перетаскивание из доступных кнопок
    if (draggedItem && draggedItem.type === 'available') {
      e.dataTransfer.dropEffect = 'copy';
      setDragOverSlot(slotIndex);
    } else {
      e.dataTransfer.dropEffect = 'none';
    }
  };

  const handleSlotDrop = (e: React.DragEvent, slotIndex: number) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!draggedItem) {
      document.body.style.overflow = '';
      setDragOverSlot(null);
      return;
    }

    setSelectedButtons((prev) => {
      const newSlots = [...prev];
      
      // Перетаскивание из слотов отключено, обрабатываем только перетаскивание из доступных кнопок
      if (draggedItem.type === 'available') {
        // Добавление из доступных кнопок
        const existingIndex = newSlots.findIndex((btn) => btn?.id === draggedItem.button.id);
        
        if (existingIndex !== -1) {
          // Если кнопка уже есть, меняем местами
          [newSlots[existingIndex], newSlots[slotIndex]] = [newSlots[slotIndex], newSlots[existingIndex]];
        } else {
          // Добавляем новую кнопку
          newSlots[slotIndex] = {
            ...draggedItem.button,
            color: '#0077FF',
          };
        }
      }
      
      return newSlots;
    });

    setDraggedItem(null);
    setDragOverSlot(null);
    setDragPosition(null);
    document.body.style.overflow = '';
  };

  const handleSlotDragLeave = () => {
    setDragOverSlot(null);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    setDragOverSlot(null);
    setDragPosition(null);
    document.body.style.overflow = '';
  };

  const removeFromSlot = (slotIndex: number) => {
    setSelectedButtons((prev) => {
      const newSlots = [...prev];
      newSlots[slotIndex] = null;
      return newSlots;
    });
  };


  if (!selectedRole) {
    return null;
  }

  // Скелетная загрузка пока загружается пользователь
  if (userLoading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="settings-section">
            {/* Скелетная загрузка для профиля */}
            <div className="card">
              <div className="card-title">Профиль</div>
              <div className="settings-profile-skeleton">
                <div className="settings-profile-email-skeleton"></div>
              </div>
              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>
                <div className="card-description" style={{ marginBottom: 12 }}>Ваш вуз</div>
                <div className="settings-university-skeleton"></div>
              </div>
            </div>

            {/* Скелетная загрузка для слотов */}
            <div className="card" style={{ marginTop: 24 }}>
              <div className="card-title">Выбранные кнопки</div>
              <div className="card-description">Перетащите кнопки для изменения порядка</div>
              <div className="settings-slots-container">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="settings-slot settings-slot-skeleton">
                    <div className="settings-slot-item-skeleton">
                      <div className="settings-slot-icon-skeleton"></div>
                      <div className="settings-slot-label-skeleton"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Скелетная загрузка для доступных кнопок */}
            <div className="card" style={{ marginTop: 24 }}>
              <div className="card-title">Доступные кнопки</div>
              <div className="card-description">Перетащите кнопки в слоты выше</div>
              <div className="settings-buttons-grid-small">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="settings-button-tile settings-button-tile-skeleton">
                    <div className="settings-button-icon-skeleton"></div>
                    <div className="settings-button-label-skeleton"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {dragGhost}
      <div className="app-container">
        <div className="container">
        <div className="settings-section">
          {/* Профиль и Вуз */}
          <div className="card">
            <div className="card-title">
              {userLoading ? 'Профиль' : 
               currentUser && currentUser.role && currentUser.role !== 'applicant' ? (
                 currentUser.role === 'student' ? 'Профиль студента' :
                 currentUser.role === 'staff' ? 'Профиль сотрудника' :
                 currentUser.role === 'admin' ? 'Профиль руководителя' :
                 'Профиль'
               ) : selectedRole === 'student' ? 'Профиль студента' :
                 selectedRole === 'staff' ? 'Профиль сотрудника' :
                 selectedRole === 'abiturient' ? 'Профиль абитуриента' :
                 'Профиль'}
            </div>
                {userLoading ? (
                  <div className="card-description">Загрузка...</div>
                ) : currentUser && currentUser.role && currentUser.role !== 'applicant' ? (
                  <div className="settings-profile">
                    <div className="settings-profile-info">
                      <div className="settings-profile-email">{currentUser.email || 'Пользователь'}</div>
                      <button
                        className="btn btn-secondary settings-logout-btn"
                        type="button"
                        onClick={async () => {
                          await logout();
                          await refresh();
                          setCurrentUser(null);
                          // Перенаправляем на страницу выбора роли
                          navigate('/');
                        }}
                        style={{ marginTop: 8 }}
                      >
                        Выйти
                      </button>
                    </div>
                  </div>
                ) : selectedRole === 'student' ? (
                  <div className="settings-profile">
                    <div className="settings-profile-info">
                      <div className="settings-profile-email">Для доступа к всему функционалу студента необходима авторизация</div>
                      <button
                        className="btn btn-primary settings-change-role-btn"
                        type="button"
                        onClick={() => {
                          navigate('/login');
                        }}
                        style={{ marginTop: 12 }}
                      >
                        Войти
                      </button>
                      <button
                        className="btn btn-secondary settings-change-role-btn"
                        type="button"
                        onClick={() => {
                          navigate('/');
                        }}
                        style={{ marginTop: 8 }}
                      >
                        Сменить роль
                      </button>
                    </div>
                  </div>
                ) : currentUser && currentUser.role === 'applicant' ? (
                  <div className="settings-profile">
                    <div className="settings-profile-info">
                      <div className="settings-profile-email">Для доступа к функциям студента или сотрудника вуза необходимо сменить роль</div>
                      <button
                        className="btn btn-primary settings-change-role-btn"
                        type="button"
                        onClick={() => {
                          navigate('/');
                        }}
                        style={{ marginTop: 12 }}
                      >
                        Сменить роль
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="settings-profile">
                    <div className="settings-profile-info">
                      <div className="settings-profile-name">Войдите в аккаунт</div>
                      <div className="settings-profile-email">Для доступа к полному функционалу</div>
                    </div>
                  </div>
                )}

            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>
              <div className="card-description" style={{ marginBottom: 12 }}>Ваш вуз</div>
              {currentUser && currentUser.role && currentUser.role !== 'applicant' ? (
                <div className="settings-university" style={{ cursor: 'default', opacity: 0.7 }}>
                  <div className="settings-university-text">
                    <div className="settings-university-name">{selectedUniversity || 'Не выбран'}</div>
                  </div>
                </div>
              ) : (
                <div className="settings-university" onClick={() => navigate('/university')}>
                  <div className="settings-university-text">
                    <div className="settings-university-name">{selectedUniversity || 'Не выбран'}</div>
                  </div>
                  <div className="settings-university-edit">
                    <Pencil size={18} />
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card" style={{ position: 'relative' }}>
            <div className="card-title">Выбранные кнопки</div>
            <div className="card-description">Перетащите кнопки в слоты ниже</div>

            {/* Overlay для сохранения */}
            {saving && (
              <div className="settings-save-overlay">
                <div className="settings-save-spinner"></div>
                <div className="settings-save-text">Сохранение...</div>
              </div>
            )}

            {/* Слоты для выбранных кнопок */}
            <div className={`settings-slots-container ${saving ? 'saving' : ''}`}>
              {selectedButtons.map((button, slotIndex) => {
                const iconElement = button?.icon ? getIcon(button.icon) : null;
                const isDragOver = dragOverSlot === slotIndex;

                return (
                  <div
                    key={slotIndex}
                    className={`settings-slot ${isDragOver ? 'drag-over' : ''} ${button ? 'filled' : 'empty'}`}
                    onDragOver={(e) => handleSlotDragOver(e, slotIndex)}
                    onDragLeave={handleSlotDragLeave}
                    onDrop={(e) => handleSlotDrop(e, slotIndex)}
                  >
                    {button ? (
                      <div
                        className="settings-slot-item"
                      >
                        {iconElement ? <div className="settings-slot-icon">{iconElement}</div> : null}
                        <span className="settings-slot-label">{button.label}</span>
                        <button
                          type="button"
                          className="settings-slot-remove"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            removeFromSlot(slotIndex);
                          }}
                          onMouseDown={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                          }}
                          onTouchStart={(e) => {
                            // Не используем preventDefault, так как это кнопка удаления
                            removeFromSlot(slotIndex);
                          }}
                          draggable={false}
                          aria-label="Удалить"
                        >
                          ×
                        </button>
                      </div>
                    ) : (
                      <div className="settings-slot-placeholder">Перетащите сюда</div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="card-title" style={{ marginTop: 24 }}>Доступные кнопки</div>
            <div className="card-description">Перетащите кнопки в слоты выше</div>

            <div className={`settings-buttons-grid-small ${saving ? 'saving' : ''}`}>
              {availableButtons
                .filter((button) => !selectedButtons.some((b) => b?.id === button.id))
                .map((button) => {
                  const iconElement = button.icon ? getIcon(button.icon) : null;
                  const isDragging = draggedItem?.type === 'available' && draggedItem.button.id === button.id;

                  return (
                    <div
                      key={button.id}
                      draggable
                      onDragStart={(e) => handleAvailableDragStart(e, button)}
                      onDragEnd={handleDragEnd}
                      onTouchStart={(e) => handleAvailableTouchStart(e, button)}
                      onTouchMove={handleTouchMove}
                      onTouchEnd={handleTouchEnd}
                      className={`settings-button-tile ${isDragging ? 'dragging' : ''}`}
                    >
                      {iconElement ? <div className="settings-button-icon-small">{iconElement}</div> : null}
                      <span className="settings-button-label-small">{button.label}</span>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}

