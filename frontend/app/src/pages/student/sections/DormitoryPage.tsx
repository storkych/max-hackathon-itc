import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { getDormitoryApplications as getDormitoryData, submitDormitoryRequest, type DormitoryApplication } from '../../../api/dormitory';

interface DormitoryService {
  id: string;
  title: string;
}

interface DormitoryPayment {
  id: string;
  residence: string;
  period: string;
  amount: number;
  status: string;
}

interface DormitoryData {
  applications: DormitoryApplication[];
  payments: DormitoryPayment[];
  services: DormitoryService[];
}

const DEFAULT_SERVICES: DormitoryService[] = [
  { id: 'service-repair', title: 'Ремонт оборудования' },
  { id: 'service-cleaning', title: 'Уборка комнаты' },
  { id: 'service-other', title: 'Другое обращение' },
];

export function DormitoryPage() {
  const [dormitoryData, setDormitoryData] = useState<DormitoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dormitoryStatus, setDormitoryStatus] = useState<'idle' | 'submitting' | 'success'>('idle');

  useEffect(() => {
    const load = async () => {
      try {
        const applications = await getDormitoryData();
        setDormitoryData({
          applications,
          payments: [],
          services: DEFAULT_SERVICES,
        });
      } catch (error) {
        console.error('Failed to load dormitory data', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleDormitorySubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());
    setDormitoryStatus('submitting');
    try {
      await submitDormitoryRequest(payload);
      const next = await getDormitoryData();
      setDormitoryData({
        applications: next,
        payments: dormitoryData?.payments ?? [],
        services: dormitoryData?.services ?? DEFAULT_SERVICES,
      });
      setDormitoryStatus('success');
      event.currentTarget.reset();
    } catch (error) {
      console.error('Failed to submit dormitory request', error);
      setDormitoryStatus('idle');
    }
  };

  if (loading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card-description">Загрузка информации об общежитии...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="container">
        <div style={{ display: 'grid', gap: 16 }}>
          {dormitoryData && dormitoryData.payments && dormitoryData.payments.length > 0 && (
            <div className="card" style={{ marginBottom: 0 }}>
              <div className="card-title">Платежи за общежитие</div>
              {dormitoryData.payments.map((payment) => (
                <div key={payment.id} className="card" style={{ marginBottom: 0 }}>
                  <strong>
                    {payment.period} • {payment.residence}
                  </strong>
                  <span>Сумма: {payment.amount.toLocaleString('ru-RU')} ₽</span>
                  <span>Статус: {payment.status === 'paid' ? 'Оплачен' : payment.status}</span>
                </div>
              ))}
            </div>
          )}

          {dormitoryData && (
            <form className="card" onSubmit={handleDormitorySubmit}>
              <div className="card-title">Создать заявку в общежитие</div>
              {dormitoryData.services && dormitoryData.services.length > 0 && (
                <div className="form-group">
                  <label className="form-label" htmlFor="dorm-service">
                    Сервис
                  </label>
                  <select className="form-input" id="dorm-service" name="service_id" required>
                    {dormitoryData.services.map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label className="form-label" htmlFor="dorm-room">
                  Комната
                </label>
                <input className="form-input" id="dorm-room" name="preferredRoom" placeholder="A-101" required />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="dorm-comment">
                  Комментарий
                </label>
                <textarea className="form-input" id="dorm-comment" name="reason" rows={3} placeholder="Опишите проблему" required />
              </div>
              <button className="btn" type="submit" disabled={dormitoryStatus === 'submitting'}>
                {dormitoryStatus === 'submitting' ? 'Отправляем...' : 'Создать заявку'}
              </button>
              {dormitoryStatus === 'success' ? (
                <div className="card-description">Заявка отправлена в службу общежития.</div>
              ) : null}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

