import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useAppState } from '../context/AppStateContext';
import { apiFetch } from '../api/httpClient';

export function LoginPage() {
  const navigate = useNavigate();
  const { selectedRole, selectedUniversity } = useAppState();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAccounts = [
    {
      label: 'Студент',
      login: 'student@example.com',
      password: 'student123',
    },
    {
      label: 'Сотрудник',
      login: 'staff@example.com',
      password: 'staff123',
    },
  ];

  useEffect(() => {
    if (!selectedRole) {
      navigate('/');
      return;
    }

    if (selectedRole === 'abiturient') {
      navigate('/dashboard/abiturient');
      return;
    }
  }, [navigate, selectedRole]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiFetch<{ user?: { id: string; email?: string; full_name?: string } }>('/auth/login', {
        method: 'POST',
        body: {
          login: email,
          password,
        },
      });

      // Проверяем наличие user в ответе - это означает успешный вход
      if (response?.user) {
        // Перенаправляем на дашборд
        if (selectedRole === 'student') {
          navigate('/dashboard/student');
        } else if (selectedRole === 'staff') {
          navigate('/dashboard/staff');
        }
      } else {
        setError('Неверный email или пароль');
      }
    } catch (err) {
      console.error('Login error', err);
      setError('Ошибка входа. Проверьте данные и попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedRole || selectedRole === 'abiturient') {
    return null;
  }

  return (
    <div className="app-container">
      <div className="container">
        <button
          type="button"
          onClick={() => navigate('/')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'none',
            border: 'none',
            color: 'var(--primary-color)',
            fontSize: 16,
            fontWeight: 500,
            cursor: 'pointer',
            padding: '8px 0',
            marginBottom: 16,
          }}
        >
          <ArrowLeft size={20} />
          Назад
        </button>

        <div className="text-center" style={{ marginBottom: 32 }}>
          <h1>Вход в личный кабинет</h1>
          <p className="subtitle">{selectedUniversity ?? 'Войдите для доступа к функциям'}</p>
        </div>

        <form className="card" onSubmit={handleSubmit}>
          {error && (
            <div className="card-description" style={{ color: 'var(--danger)', marginBottom: 16 }}>
              {error}
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email
            </label>
            <input
              className="form-input"
              id="email"
              type="email"
              placeholder="student@university.ru"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Пароль
            </label>
            <input
              className="form-input"
              id="password"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button className="btn" type="submit" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-title">Вход в тестовые аккаунты</div>
          <div className="card-description" style={{ marginBottom: 12 }}>
            Быстрый вход для демонстрации разных ролей
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {testAccounts.map((account) => (
              <button
                key={account.login}
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setEmail(account.login);
                  setPassword(account.password);
                  setError(null);
                }}
                disabled={loading}
                style={{ justifyContent: 'space-between', display: 'flex', alignItems: 'center' }}
              >
                <span>{account.label}</span>
                <span style={{ fontSize: 12, opacity: 0.8 }}>{account.login}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

