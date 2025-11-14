/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { useAppState } from './AppStateContext';
import { getBottomNavSettings, saveBottomNavSettings, type BottomNavButton } from '../api/settings';
import { getDefaultBottomNavButtons } from '../utils/bottomNavDefaults';
import { fetchCurrentUser } from '../api/auth';
import { filterButtonsForRole } from '../utils/bottomNavConfig';

interface BottomNavContextValue {
  buttons: BottomNavButton[];
  loading: boolean;
  updateButtons: (newButtons: BottomNavButton[]) => Promise<void>;
  refresh: () => Promise<void>;
}

const BottomNavContext = createContext<BottomNavContextValue | undefined>(undefined);

export function BottomNavProvider({ children }: { children: ReactNode }) {
  const { selectedRole } = useAppState();
  const [buttons, setButtons] = useState<BottomNavButton[]>([]);
  const [loading, setLoading] = useState(true);
  const [studentAuthenticated, setStudentAuthenticated] = useState<boolean | undefined>(undefined);

  const resolveStudentAuth = useCallback(async () => {
    if (selectedRole !== 'student') {
      setStudentAuthenticated(undefined);
      return undefined;
    }
    try {
      const user = await fetchCurrentUser();
      const isAuth = Boolean(user?.role && user.role !== 'applicant');
      setStudentAuthenticated(isAuth);
      return isAuth;
    } catch (error) {
      console.warn('Failed to resolve student auth state', error);
      setStudentAuthenticated(false);
      return false;
    }
  }, [selectedRole]);

  const loadSettings = useCallback(async () => {
    if (!selectedRole) {
      setButtons([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const [settings, studentAuth] = await Promise.all([getBottomNavSettings(), resolveStudentAuth()]);
      const baseButtons = settings.length > 0 ? settings : getDefaultBottomNavButtons(selectedRole);
      const sanitizedButtons = filterButtonsForRole(baseButtons, selectedRole, {
        isStudentAuthenticated: studentAuth,
      });

      if (sanitizedButtons.length !== baseButtons.length) {
        await saveBottomNavSettings(sanitizedButtons);
      }

      setButtons(sanitizedButtons);
    } catch (error) {
      console.warn('Failed to load bottom nav settings, using defaults', error);
      const defaults = getDefaultBottomNavButtons(selectedRole);
      const sanitizedDefaults = filterButtonsForRole(defaults, selectedRole, {
        isStudentAuthenticated: selectedRole === 'student' ? false : undefined,
      });
      setButtons(sanitizedDefaults);
    } finally {
      setLoading(false);
    }
  }, [selectedRole, resolveStudentAuth]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const updateButtons = useCallback(
    async (newButtons: BottomNavButton[]) => {
      if (!selectedRole) {
        return;
      }

      try {
        const sanitized = filterButtonsForRole(newButtons, selectedRole, {
          isStudentAuthenticated: studentAuthenticated,
        });
        await saveBottomNavSettings(sanitized);
        setButtons(sanitized);
      } catch (error) {
        console.error('Failed to save bottom nav settings', error);
        throw error;
      }
    },
    [selectedRole, studentAuthenticated],
  );

  const value: BottomNavContextValue = {
    buttons,
    loading,
    updateButtons,
    refresh: loadSettings,
  };

  return <BottomNavContext.Provider value={value}>{children}</BottomNavContext.Provider>;
}

export function useBottomNavContext() {
  const context = useContext(BottomNavContext);
  if (!context) {
    throw new Error('useBottomNavContext must be used within a BottomNavProvider');
  }
  return context;
}

