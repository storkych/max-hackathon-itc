# Max Campus Frontend (React + Vite + TypeScript)

Одностраничное приложение для мини-приложения Max Campus. Реализованы все экраны из HTML-прототипов (выбор вуза, роли и четыре дашборда) с использованием моковых данных, повторяющих контракты API из `max-campus-api.postman_collection.json`.

## Быстрый старт

```bash
cd app
npm install
npm run dev
```

По умолчанию приложение открывается на порту `5173`. Сборка для продакшена: `npm run build`.

## Структура

- `src/pages` – страницы и дашборды для всех ролей (`abiturient`, `student`, `staff`, `admin`).
- `src/components` – переиспользуемые компоненты (`DashboardLayout`, `NavBar`, `MockModeToggle`).
- `src/context/AppStateContext.tsx` – хранение выбранного вуза, роли и состояния mock-режима (значения кешируются в `localStorage`).
- `src/mocks/mockData.ts` – эталонные ответы для всех задокументированных ручек.
- `src/mocks/mockApi.ts` – слой, имитирующий запросы к API (Promise + задержка + логирование payload).

## Mock-режим

В правой части навигации отображается переключатель «Mock данные». Пока серверные ручки не доступны, всё приложение работает только в mock-режиме, но переключатель уже встроен в контекст и маршруты. Как только API заработает:

1. Добавьте реальные реализации в слой `src/mocks/mockApi.ts` (или создайте рядом `services/api.ts`) и переключайте их в зависимости от `mockMode`.
2. Благодаря единой точке входа заменить данные можно без переписывания страниц.

## Соответствие API

Для каждого раздела дашбордов использованы мок-данные, повторяющие структуры из Postman-коллекции:

- Поступление: `GET /admissions/*`, `POST /admissions/open-days/registrations`, `POST /admissions/inquiries`.
- Студенты: расписания, элективы, проекты, карьера, деканат, общежитие, события, библиотека.
- Сотрудники: командировки, отпуска, HR-справки, гостевые пропуска.
- Руководитель: дашборды, академические метрики, мониторинг новостей.

Все формы имеют состояния отправки/успеха и готовы к замене на настоящие fetch-запросы.

## Дальнейшие шаги

- Подключить реальные эндпоинты (замена реализаций в `mockApi.ts`).
- Добавить авторизацию и работу с токеном из Postman-переменных.
- Подключить систему уведомлений вместо in-place сообщений.
- Настроить тестирование (React Testing Library / Playwright) для ключевых сценариев.

## API configuration

The app now consumes the real API available at `https://student-app-api.itc-hub.ru/api/v1` for the Auth and Admissions sections.

Create a `.env.local` file inside the `app` directory to override defaults:

```
VITE_API_BASE_URL=https://student-app-api.itc-hub.ru/api/v1
VITE_API_ACCESS_TOKEN=your_jwt_token
```

If `VITE_API_ACCESS_TOKEN` is not provided, the client will try to reuse a token from `localStorage` under the `api_access_token` key. Admissions fetches automatically fall back to mock data when the network call fails so that the UI remains functional offline.
