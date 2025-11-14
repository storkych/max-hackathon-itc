/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useMemo, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export type UserRole = 'abiturient' | 'student' | 'staff' | 'admin';

export interface AppStateContextValue {
  selectedUniversityId: string | null;
  selectedUniversity: string | null;
  setSelectedUniversity: (university: { id: string; name: string } | null) => void;
  selectedRole: UserRole | null;
  setSelectedRole: (role: UserRole | null) => void;
  resetState: () => void;
}

const STORAGE_KEY = 'max-campus-app-state';

interface PersistedState {
  selectedUniversityId: string | null;
  selectedUniversity: string | null;
  selectedRole: UserRole | null;
}

const defaultState: PersistedState = {
  selectedUniversityId: null,
  selectedUniversity: null,
  selectedRole: null,
};

const AppStateContext = createContext<AppStateContextValue | undefined>(undefined);

function loadState(): PersistedState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return defaultState;
    }
    const parsed = JSON.parse(stored) as PersistedState;
    return {
      selectedUniversityId: parsed.selectedUniversityId ?? defaultState.selectedUniversityId,
      selectedUniversity: parsed.selectedUniversity ?? defaultState.selectedUniversity,
      selectedRole: parsed.selectedRole ?? defaultState.selectedRole,
    };
  } catch (error) {
    console.warn('Failed to load app state from localStorage', error);
    return defaultState;
  }
}

function persistState(state: PersistedState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn('Failed to persist app state', error);
  }
}

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [selectedUniversityId, setSelectedUniversityId] = useState<string | null>(() => loadState().selectedUniversityId);
  const [selectedUniversity, setSelectedUniversityState] = useState<string | null>(() => loadState().selectedUniversity);
  const [selectedRole, setSelectedRoleState] = useState<UserRole | null>(() => loadState().selectedRole);

  useEffect(() => {
    persistState({ selectedUniversityId, selectedUniversity, selectedRole });
  }, [selectedUniversityId, selectedUniversity, selectedRole]);

  const value = useMemo<AppStateContextValue>(() => {
    const setSelectedUniversity = (university: { id: string; name: string } | null) => {
      setSelectedUniversityId(university?.id ?? null);
      setSelectedUniversityState(university?.name ?? null);
    };
    const setSelectedRole = (role: UserRole | null) => setSelectedRoleState(role);
    const resetState = () => {
      setSelectedUniversityId(null);
      setSelectedUniversityState(null);
      setSelectedRoleState(null);
    };

    return {
      selectedUniversityId,
      selectedUniversity,
      setSelectedUniversity,
      selectedRole,
      setSelectedRole,
      resetState,
    };
  }, [selectedUniversityId, selectedUniversity, selectedRole]);

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
}

