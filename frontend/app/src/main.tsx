import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App.tsx';
import { AppStateProvider } from './context/AppStateContext';
import { BottomNavProvider } from './context/BottomNavContext';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppStateProvider>
      <BrowserRouter>
        <BottomNavProvider>
          <App />
        </BottomNavProvider>
      </BrowserRouter>
    </AppStateProvider>
  </StrictMode>,
);

const { WebApp } = globalThis as typeof globalThis & {
  WebApp?: {
    ready?: () => void;
    initData?: unknown;
    initDataUnsafe?: unknown;
  };
};

if (WebApp) {
  WebApp.ready?.();
  const webAppData =
    WebApp.initDataUnsafe !== undefined ? WebApp.initDataUnsafe : WebApp.initData ?? null;
  console.log('MAX WebAppData', webAppData);
  console.log('WebApp.initData', WebApp.initData);
} else {
  console.warn('MAX WebApp не обнаружен. Проверьте подключение скрипта max-web-app.js.');
}
