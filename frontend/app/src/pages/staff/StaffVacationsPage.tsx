import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { getMyLeaveRequests, submitLeaveRequest, type LeaveRequest, type LeaveRequestPayload } from '../../api/hr';
import { formatRange, formatStatus, type HrStatus } from './hrUtils';

export function StaffVacationsPage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<HrStatus>('idle');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const list = await getMyLeaveRequests();
      setRequests(list);
      setError(null);
    } catch (refreshError) {
      console.error('Failed to load leave requests', refreshError);
      setError('Не удалось загрузить список отпусков.');
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
    const payload: LeaveRequestPayload = {
      leave_type: String(formData.get('leave_type') ?? 'vacation'),
      start_date: String(formData.get('start_date') ?? ''),
      end_date: String(formData.get('end_date') ?? ''),
      replacement: formData.get('replacement_name')
        ? {
            full_name: String(formData.get('replacement_name') ?? ''),
            contacts: String(formData.get('replacement_contacts') ?? ''),
          }
        : undefined,
    };

    setStatus('submitting');
    try {
      await submitLeaveRequest(payload);
      await refresh();
      setStatus('success');
      setError(null);
      event.currentTarget.reset();
    } catch (submitError) {
      console.error('Failed to submit leave request', submitError);
      setStatus('error');
      setError('Не удалось отправить заявку на отпуск.');
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Отпуска</h1>
            <p className="subtitle">Планируйте отпуска и отслеживайте статус согласования заявок.</p>
          </div>
        </div>

        {error && <div className="card-description" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

        <div style={{ display: 'grid', gap: 16 }}>
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title">Мои отпуска</div>
            {loading ? (
              <div className="card-description">Загрузка...</div>
            ) : requests.length === 0 ? (
              <div className="card-description">Заявок пока нет.</div>
            ) : (
              <div style={{ display: 'grid', gap: 12 }}>
                {requests.map((leave) => (
                  <div key={leave.id} className="card" style={{ marginBottom: 0 }}>
                    <strong>
                      {leave.type === 'vacation' ? 'Ежегодный отпуск' : leave.type === 'sick' ? 'Больничный' : 'Отпуск'}
                    </strong>
                    <span>{formatRange(leave.startDate, leave.endDate)}</span>
                    <span>Статус: {formatStatus(leave.status)}</span>
                    {leave.replacement?.fullName ? <span>Замещающий: {leave.replacement.fullName}</span> : null}
                  </div>
                ))}
              </div>
            )}
          </div>

          <form className="card" onSubmit={handleSubmit}>
            <div className="card-title">Подать заявку на отпуск</div>
            <div className="form-group">
              <label className="form-label" htmlFor="leave-type">
                Тип отпуска
              </label>
              <select className="form-input" id="leave-type" name="leave_type" defaultValue="vacation">
                <option value="vacation">Ежегодный</option>
                <option value="sick">Больничный</option>
                <option value="unpaid">Без содержания</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="leave-start">
                Начало отпуска
              </label>
              <input className="form-input" id="leave-start" type="date" name="start_date" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="leave-end">
                Конец отпуска
              </label>
              <input className="form-input" id="leave-end" type="date" name="end_date" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="replacement-name">
                Замещающий сотрудник (опционально)
              </label>
              <input className="form-input" id="replacement-name" name="replacement_name" placeholder="Анна Смирнова" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="replacement-contacts">
                Контакты замены
              </label>
              <input className="form-input" id="replacement-contacts" name="replacement_contacts" placeholder="anna@example.com" />
            </div>
            <button className="btn" type="submit" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Отправляем...' : 'Отправить заявку'}
            </button>
            {status === 'success' ? <div className="card-description">Заявка отправлена руководителю.</div> : null}
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

