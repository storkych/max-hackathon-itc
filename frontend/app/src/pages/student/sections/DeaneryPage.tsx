import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import {
  getDeaneryRequests as getDeaneryData,
  submitDeaneryRequest,
  type DeaneryRequest,
  type DeaneryRequestPayload,
} from '../../../api/deanery';

export function DeaneryPage() {
  const [requests, setRequests] = useState<DeaneryRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [deaneryStatus, setDeaneryStatus] = useState<'idle' | 'submitting' | 'success'>('idle');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getDeaneryData();
        setRequests(data);
      } catch (error) {
        console.error('Failed to load deanery data', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleDeanerySubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const getValue = (name: string) => {
      const value = formData.get(name);
      if (typeof value === 'string') {
        return value;
      }
      if (value == null) {
        return undefined;
      }
      return String(value);
    };
    const payload: DeaneryRequestPayload = {
      type: getValue('type') ?? 'study_place',
      description: getValue('description') || undefined,
    };
    const language = getValue('language');
    if (language) {
      payload.language = language;
    }
    setDeaneryStatus('submitting');
    try {
      await submitDeaneryRequest(payload);
      const next = await getDeaneryData();
      setRequests(next);
      setDeaneryStatus('success');
      event.currentTarget.reset();
    } catch (error) {
      console.error('Failed to submit deanery request', error);
      setDeaneryStatus('idle');
    }
  };

  if (loading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card-description">Загрузка данных деканата...</div>
        </div>
      </div>
    );
  }

  const certificateTypeLabels: Record<string, string> = {
    study_place: 'С места учебы',
    scholarship: 'Для стипендии',
    visa: 'Для визы / консульства',
    military: 'Для военкомата',
    dormitory: 'Для общежития',
  };

  const getStatusLabel = (status?: string) => {
    if (!status) return 'В обработке';
    if (status === 'ready') return 'Готово';
    if (status === 'rejected') return 'Отклонено';
    if (status === 'pending') return 'В обработке';
    return status;
  };

  return (
    <div className="app-container">
      <div className="container">
        <div style={{ display: 'grid', gap: 16 }}>
          <form className="card" onSubmit={handleDeanerySubmit}>
            <div className="card-title">Запросить справку</div>
            <div className="form-group">
              <label className="form-label" htmlFor="certificate-type">
                Тип справки
              </label>
              <select className="form-input" id="certificate-type" name="type" required defaultValue="study_place">
                <option value="study_place">С места учебы</option>
                <option value="scholarship">Для стипендии</option>
                <option value="visa">Для визы / консульства</option>
                <option value="military">Для военкомата</option>
                <option value="dormitory">Для общежития</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="certificate-language">
                Язык
              </label>
              <select className="form-input" id="certificate-language" name="language" defaultValue="ru" required>
                <option value="ru">Русский</option>
                <option value="en">Английский</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="certificate-purpose">
                Назначение
              </label>
              <input className="form-input" id="certificate-purpose" name="description" placeholder="Для работодателя" required />
            </div>
            <button className="btn" type="submit" disabled={deaneryStatus === 'submitting'}>
              {deaneryStatus === 'submitting' ? 'Отправляем...' : 'Отправить запрос'}
            </button>
            {deaneryStatus === 'success' ? (
              <div className="card-description">Справка будет готова в течение 3 рабочих дней.</div>
            ) : null}
          </form>

          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title">Мои запросы</div>
            {requests.length === 0 ? (
              <div className="card-description">Запросов пока нет. Отправьте первый запрос через форму выше.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {requests.map((certificate) => (
                  <div key={certificate.id} className="deanery-request-card">
                    <div className="deanery-request-header">
                      <strong>{certificateTypeLabels[certificate.type ?? 'study_place'] ?? certificate.type ?? 'Справка'}</strong>
                      <span className={`deanery-status deanery-status--${certificate.status ?? 'pending'}`}>
                        {getStatusLabel(certificate.status)}
                      </span>
                    </div>
                    <div className="deanery-request-meta">
                      <span>Запрошена: {new Date(certificate.submittedAt ?? Date.now()).toLocaleDateString('ru-RU')}</span>
                      {certificate.response && <span>Комментарий: {certificate.response}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

