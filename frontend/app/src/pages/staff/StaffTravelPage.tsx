import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { getMyTravelRequests, submitTravelRequest, type TravelRequest, type TravelRequestPayload } from '../../api/hr';
import { formatRange, formatStatus, type HrStatus } from './hrUtils';

export function StaffTravelPage() {
  const { selectedUniversity } = useAppState();
  const navigate = useNavigate();

  const [requests, setRequests] = useState<TravelRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<HrStatus>('idle');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const list = await getMyTravelRequests();
      setRequests(list);
      setError(null);
    } catch (refreshError) {
      console.error('Failed to load travel requests', refreshError);
      setError('Не удалось загрузить список командировок.');
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
    const payload: TravelRequestPayload = {
      title: String(formData.get('title') ?? ''),
      purpose: String(formData.get('purpose') ?? ''),
      destination: {
        city: String(formData.get('destination_city') ?? ''),
        country: String(formData.get('destination_country') ?? '') || undefined,
      },
      start_date: String(formData.get('start_date') ?? ''),
      end_date: String(formData.get('end_date') ?? ''),
      transport: {
        type: String(formData.get('transport_type') ?? 'train'),
        class: String(formData.get('transport_class') ?? 'standard'),
      },
      accommodations: formData.get('hotel_name')
        ? [
            {
              hotel: String(formData.get('hotel_name') ?? ''),
              check_in: String(formData.get('hotel_check_in') ?? formData.get('start_date') ?? ''),
              check_out: String(formData.get('hotel_check_out') ?? formData.get('end_date') ?? ''),
            },
          ]
        : undefined,
      expenses_plan: formData.get('expense_amount')
        ? [
            {
              category: String(formData.get('expense_category') ?? 'прочее'),
              amount: Number(formData.get('expense_amount')),
              currency: String(formData.get('expense_currency') ?? 'RUB'),
            },
          ]
        : undefined,
    };

    setStatus('submitting');
    try {
      await submitTravelRequest(payload);
      await refresh();
      setStatus('success');
      setError(null);
      event.currentTarget.reset();
    } catch (submitError) {
      console.error('Failed to submit travel request', submitError);
      setStatus('error');
      setError('Не удалось отправить запрос на командировку.');
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Командировки</h1>
            <p className="subtitle">Отправляйте запросы на командировки и отслеживайте их статусы.</p>
          </div>
        </div>

        {error && <div className="card-description" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

        <div style={{ display: 'grid', gap: 16 }}>
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title">Мои командировки</div>
            {loading ? (
              <div className="card-description">Загрузка...</div>
            ) : requests.length === 0 ? (
              <div className="card-description">У вас ещё нет командировок.</div>
            ) : (
              <div style={{ display: 'grid', gap: 12 }}>
                {requests.map((request) => (
                  <div key={request.id} className="card" style={{ marginBottom: 0 }}>
                    <strong>{request.title}</strong>
                    <span>
                      {request.destination?.city ?? 'Город не указан'}
                      {request.destination?.country ? ` • ${request.destination.country}` : ''}
                    </span>
                    <span>{formatRange(request.startDate, request.endDate)}</span>
                    <span>Статус: {formatStatus(request.status)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <form className="card" onSubmit={handleSubmit}>
            <div className="card-title">Создать запрос</div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-title">
                Название поездки
              </label>
              <input className="form-input" id="travel-title" name="title" placeholder="Digital Forum 2024" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-purpose">
                Цель
              </label>
              <input className="form-input" id="travel-purpose" name="purpose" placeholder="Выступление с докладом" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-city">
                Город назначения
              </label>
              <input className="form-input" id="travel-city" name="destination_city" placeholder="Казань" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-country">
                Страна
              </label>
              <input className="form-input" id="travel-country" name="destination_country" placeholder="Россия" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-start">
                Дата начала
              </label>
              <input className="form-input" id="travel-start" type="date" name="start_date" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="travel-end">
                Дата окончания
              </label>
              <input className="form-input" id="travel-end" type="date" name="end_date" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="transport-type">
                Транспорт
              </label>
              <select className="form-input" id="transport-type" name="transport_type" defaultValue="train">
                <option value="train">Поезд</option>
                <option value="plane">Самолёт</option>
                <option value="car">Автомобиль</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="transport-class">
                Класс
              </label>
              <input className="form-input" id="transport-class" name="transport_class" placeholder="Эконом" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="hotel-name">
                Отель (опционально)
              </label>
              <input className="form-input" id="hotel-name" name="hotel_name" placeholder="Отель Центральный" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="hotel-check-in">
                Заселение
              </label>
              <input className="form-input" id="hotel-check-in" type="date" name="hotel_check_in" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="hotel-check-out">
                Выезд
              </label>
              <input className="form-input" id="hotel-check-out" type="date" name="hotel_check_out" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="expense-category">
                Статья расходов
              </label>
              <input className="form-input" id="expense-category" name="expense_category" placeholder="Суточные" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="expense-amount">
                Сумма (₽)
              </label>
              <input className="form-input" id="expense-amount" type="number" min="0" step="100" name="expense_amount" placeholder="5000" />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="expense-currency">
                Валюта
              </label>
              <input className="form-input" id="expense-currency" name="expense_currency" placeholder="RUB" />
            </div>

            <button className="btn" type="submit" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Отправляем...' : 'Отправить на согласование'}
            </button>
            {status === 'success' ? <div className="card-description">Запрос создан и отправлен ответственному.</div> : null}
            {status === 'error' ? (
              <div className="card-description" style={{ color: 'var(--danger)' }}>
                Проверьте поля и попробуйте снова.
              </div>
            ) : null}
          </form>
        </div>
      </div>
    </div>
  );
}

