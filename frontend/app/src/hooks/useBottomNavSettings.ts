import { useEffect, useState } from 'react';
import { useAppState } from '../context/AppStateContext';
import { getBottomNavSettings, saveBottomNavSettings, type BottomNavButton } from '../api/settings';
import { getDefaultBottomNavButtons } from '../utils/bottomNavDefaults';

export function useBottomNavSettings() {
  const { selectedRole } = useAppState();
  const [buttons, setButtons] = useState<BottomNavButton[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const loadSettings = async () => {
    if (!selectedRole) {
      setButtons([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const settings = await getBottomNavSettings();
      setButtons(settings.length > 0 ? settings : getDefaultBottomNavButtons(selectedRole));
    } catch (error) {
      console.warn('Failed to load bottom nav settings, using defaults', error);
      setButtons(getDefaultBottomNavButtons(selectedRole));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      if (!selectedRole) {
        setButtons([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const settings = await getBottomNavSettings();
        if (mounted) {
          setButtons(settings.length > 0 ? settings : getDefaultBottomNavButtons(selectedRole));
        }
      } catch (error) {
        console.warn('Failed to load bottom nav settings, using defaults', error);
        if (mounted) {
          setButtons(getDefaultBottomNavButtons(selectedRole));
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, [selectedRole, refreshKey]);

  const updateButtons = async (newButtons: BottomNavButton[]) => {
    if (!selectedRole) {
      return;
    }

    try {
      await saveBottomNavSettings(newButtons);
      setButtons(newButtons);
      // Триггерим перезагрузку для всех экземпляров хука
      setRefreshKey((prev) => prev + 1);
    } catch (error) {
      console.error('Failed to save bottom nav settings', error);
      throw error;
    }
  };

  return { buttons, loading, updateButtons, refresh: loadSettings };
}

