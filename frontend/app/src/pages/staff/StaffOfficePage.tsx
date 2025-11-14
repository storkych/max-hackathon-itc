import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { getMyGuestPasses, submitGuestPass, type GuestPass, type GuestPassPayload } from '../../api/hr';
import { formatRange, formatStatus, normalizeTimeInput, type HrStatus } from './hrUtils';

export function StaffOfficePage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  const [passes, setPasses] = useState<GuestPass[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<HrStatus>('idle');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const list = await getMyGuestPasses();
      setPasses(list);
      setError(null);
    } catch (refreshError) {
      console.error('Failed to load guest passes', refreshError);
      setError('Не удалось загрузить гостевые пропуска.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!selectedUniversity) {
      navigate('/');
      return;
    }
    refresh();
  }, [selectedUniversity, navigate, refresh]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload: GuestPassPayload = {
      guest_full_name: String(formData.get('guest_full_name') ?? ''),
      guest_company: String(formData.get('guest_company') ?? ''),
      visit_date: String(formData.get('visit_date') ?? ''),
      visit_time_from: normalizeTimeInput(String(formData.get('visit_time_from') ?? '')),
      visit_time_to: normalizeTimeInput(String(formData.get('visit_time_to') ?? '')),
      notes: String(formData.get('notes') ?? '') || undefined,
    };

    setStatus('submitting');
    try {
      await submitGuestPass(payload);
      await refresh();
      setStatus('success');
      setError(null);
      event.currentTarget.reset();
    } catch (submitError) {
      console.error('Failed to submit guest pass', submitError);
      setStatus('error');
      setError('Не удалось оформить гостевой пропуск.');
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Офис и HR</h1>
            <p className="subtitle">Оформляйте гостевые пропуска для партнёров и отслеживайте отправленные запросы.</p>
          </div>
        </div>

        {error && <div className="card-description" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

        <div style={{ display: 'grid', gap: 16 }}>
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title">Мои гостевые пропуска</div>
            {loading ? (
              <div className="card-description">Загрузка...</div>
            ) : passes.length === 0 ? (
              <div className="card-description">Вы ещё не оформляли пропуска.</div>
            ) : (
              <div style={{ display: 'grid', gap: 12 }}>
                {passes.map((pass) => (
                  <div key={pass.id} className="card" style={{ marginBottom: 0 }}>
                    <strong>{pass.guestFullName}</strong>
                    <span>{pass.guestCompany ?? 'Компания не указана'}</span>
                    <span>
                      {formatRange(pass.visitDate, pass.visitDate)} • {pass.visitTimeFrom ?? '—'} — {pass.visitTimeTo ?? '—'}
                    </span>
                    <span>Статус: {formatStatus(pass.status)}</span>
                    {pass.notes ? <span>Примечание: {pass.notes}</span> : null}
                  </div>
                ))}
              </div>
            )}
          </div>

          <form className="card" onSubmit={handleSubmit}>
            <div className="card-title">Оформить гостевой пропуск</div>
            <div className="form-group">
              <label className="form-label" htmlFor="guest-full-name">
                ФИО гостя
              </label>
              <input className="form-input" id="guest-full-name" name="guest_full_name" placeholder="Алексей Иванов" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="guest-company">
                Компания
              </label>
              <input className="form-input" id="guest-company" name="guest_company" placeholder="Partner LLC" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="visit-date">
                Дата визита
              </label>
              <input className="form-input" id="visit-date" type="date" name="visit_date" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="visit-time-from">
                Время с
              </label>
              <input className="form-input" id="visit-time-from" type="time" name="visit_time_from" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="visit-time-to">
                Время до
              </label>
              <input className="form-input" id="visit-time-to" type="time" name="visit_time_to" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="visit-notes">
                Примечание
              </label>
              <input className="form-input" id="visit-notes" name="notes" placeholder="Встреча по проекту" />
            </div>

            <button className="btn" type="submit" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Отправляем...' : 'Оформить пропуск'}
            </button>
            {status === 'success' ? <div className="card-description">Запрос отправлен службе безопасности.</div> : null}
            {status === 'error' ? (
              <div className="card-description" style={{ color: 'var(--danger)' }}>
                Проверьте данные и попробуйте снова.
              </div>
            ) : null}
          </form>
        </div>
      </div>
    </div>
  );
}

