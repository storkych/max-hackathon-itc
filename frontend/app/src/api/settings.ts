import { apiFetch } from './httpClient';

export interface BottomNavButton {
  id: string;
  label: string;
  icon?: string;
  route: string;
  color?: string;
}

export interface UserSettings {
  bottomNav?: {
    buttons?: BottomNavButton[];
    color?: string;
  };
  isFirstTime?: boolean;
  [key: string]: unknown; // Для других будущих настроек
}

interface SettingsResponse {
  settings?: UserSettings;
}

export async function getUserSettings(): Promise<UserSettings> {
  try {
    const response = await apiFetch<SettingsResponse>('/users/settings');
    // Сервер возвращает { settings: {...} }, извлекаем settings
    return response?.settings ?? {};
  } catch (error) {
    // Если ручка еще не готова, возвращаем пустой объект
    console.warn('Failed to fetch user settings', error);
    return {};
  }
}

export async function saveUserSettings(settings: UserSettings): Promise<void> {
  // Сервер ожидает структуру { settings: {...} }
  await apiFetch('/users/settings', {
    method: 'POST',
    body: {
      settings,
    },
  });
}

// Вспомогательные функции для работы с bottom-nav
export async function getBottomNavSettings(): Promise<BottomNavButton[]> {
  const settings = await getUserSettings();
  return settings.bottomNav?.buttons ?? [];
}

export async function saveBottomNavSettings(buttons: BottomNavButton[]): Promise<void> {
  const currentSettings = await getUserSettings();
  await saveUserSettings({
    ...currentSettings,
    bottomNav: {
      buttons,
      color: buttons[0]?.color,
    },
  });
}

// Функции для работы с isFirstTime
export async function getIsFirstTime(): Promise<boolean> {
  const settings = await getUserSettings();
  // Если поле не установлено, считаем что это первый раз
  const isFirstTime = settings.isFirstTime !== false;
  console.log('[Settings] getIsFirstTime:', {
    isFirstTime,
    settingsValue: settings.isFirstTime,
    settings,
  });
  return isFirstTime;
}

export async function setIsFirstTime(isFirstTime: boolean): Promise<void> {
  console.log('[Settings] setIsFirstTime:', {
    isFirstTime,
    previousSettings: await getUserSettings(),
  });
  const currentSettings = await getUserSettings();
  await saveUserSettings({
    ...currentSettings,
    isFirstTime,
  });
  console.log('[Settings] setIsFirstTime: saved successfully');
}

