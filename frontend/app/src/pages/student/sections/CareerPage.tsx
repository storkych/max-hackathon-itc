import { useEffect, useState, useMemo } from 'react';
import type { FormEvent } from 'react';
import { getCareerConsultations, submitCareerConsultationRequest, type CareerConsultation } from '../../../api/careers';

export function CareerPage() {
  const [consultations, setConsultations] = useState<CareerConsultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [careerStatus, setCareerStatus] = useState<'idle' | 'submitting' | 'success'>('idle');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getCareerConsultations();
        setConsultations(data);
      } catch (error) {
        console.error('Failed to load career consultations', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const upcomingConsultations = useMemo(
    () => consultations.filter((item) => item.status !== 'completed'),
    [consultations],
  );

  const handleCareerSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());
    setCareerStatus('submitting');
    try {
      await submitCareerConsultationRequest(payload);
      const next = await getCareerConsultations();
      setConsultations(next);
      setCareerStatus('success');
      event.currentTarget.reset();
    } catch (error) {
      console.error('Failed to submit career consultation', error);
      setCareerStatus('idle');
    }
  };

  if (loading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card-description">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="container">
        <div style={{ display: 'grid', gap: 16 }}>
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title">Назначенные консультации</div>
            <div style={{ display: 'grid', gap: 12 }}>
              {upcomingConsultations.length === 0 ? (
                <div className="card-description">Нет активных консультаций.</div>
              ) : (
                upcomingConsultations.map((consultation) => (
                  <div key={consultation.id} className="card" style={{ marginBottom: 0 }}>
                    <strong>{consultation.topic}</strong>
                    {consultation.mentor && <span>Ментор: {consultation.mentor}</span>}
                    <span>
                      Статус: {consultation.status === 'scheduled' ? 'Запланирована' : consultation.status}
                    </span>
                    {consultation.slot && <span>Слот: {consultation.slot}</span>}
                    {consultation.channel && <span>Канал: {consultation.channel}</span>}
                  </div>
                ))
              )}
            </div>
          </div>

          <form className="card" onSubmit={handleCareerSubmit}>
            <div className="card-title">Запросить консультацию</div>
            <div className="form-group">
              <label className="form-label" htmlFor="career-topic">
                Тема
              </label>
              <input className="form-input" id="career-topic" name="topic" placeholder="Подготовка к собеседованию" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="career-subtopic">
                Подтема
              </label>
              <input className="form-input" id="career-subtopic" name="subtopic" placeholder="Product Manager" required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="career-slots">
                Предпочитаемые слоты
              </label>
              <textarea className="form-input" id="career-slots" name="preferred_slots" rows={3} placeholder="2024-11-15 10:00-11:00" required />
            </div>
            <button className="btn" type="submit" disabled={careerStatus === 'submitting'}>
              {careerStatus === 'submitting' ? 'Отправляем...' : 'Отправить запрос'}
            </button>
            {careerStatus === 'success' ? (
              <div className="card-description">Заявка отправлена. Специалист центра карьеры свяжется с вами.</div>
            ) : null}
          </form>
        </div>
      </div>
    </div>
  );
}

