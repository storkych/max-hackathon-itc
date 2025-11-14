import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { getAdmissionsPrograms, submitAdmissionInquiry, type AdmissionsProgram } from '../../../api/admissions';
import { useAppState } from '../../../context/AppStateContext';

type Status = 'idle' | 'submitting' | 'success' | 'error';

const generateAttachmentId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `attachment-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const ADMISSION_TOPICS = [
  { id: 'admission', title: 'Условия поступления' },
  { id: 'documents', title: 'Документы и сроки' },
  { id: 'scholarships', title: 'Стипендии и льготы' },
  { id: 'dormitory', title: 'Общежитие' },
  { id: 'other', title: 'Другой вопрос' },
];

export function AdmissionInquiryPage() {
  const { selectedUniversityId } = useAppState();
  const [inquiryStatus, setInquiryStatus] = useState<Status>('idle');
  const [error, setError] = useState<string | null>(null);
  const [programs, setPrograms] = useState<AdmissionsProgram[]>([]);
  const [attachments, setAttachments] = useState<Array<{ id: string; name: string; url: string }>>([
    { id: generateAttachmentId(), name: '', url: '' },
  ]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      if (!selectedUniversityId) {
        return;
      }
      try {
        const { programs: programsResponse } = await getAdmissionsPrograms(selectedUniversityId);
        if (mounted) {
          setPrograms(programsResponse);
        }
      } catch (loadError) {
        console.error('Failed to load programs for inquiry form', loadError);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [selectedUniversityId]);

  const handleAttachmentChange = (attachmentId: string, field: 'name' | 'url', value: string) => {
    setAttachments((prev) => prev.map((item) => (item.id === attachmentId ? { ...item, [field]: value } : item)));
  };

  const addAttachment = () => {
    setAttachments((prev) => [...prev, { id: generateAttachmentId(), name: '', url: '' }]);
  };

  const removeAttachment = (attachmentId: string) => {
    setAttachments((prev) => prev.filter((item) => item.id !== attachmentId));
  };

  const handleInquirySubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const rawEntries = Object.fromEntries(formData.entries()) as Record<string, FormDataEntryValue>;

    const consentValue = rawEntries['consents.personal_data'];
    const consentString = typeof consentValue === 'string' ? consentValue : '';
    const payload: Record<string, unknown> = {
      full_name: String(rawEntries.full_name ?? ''),
      email: String(rawEntries.email ?? ''),
      phone: String(rawEntries.phone ?? ''),
      topic: String(rawEntries.topic ?? ''),
      question: String(rawEntries.question ?? ''),
      university_id: selectedUniversityId,
      program_id: rawEntries.program_id ? String(rawEntries.program_id) : undefined,
      consents: {
        personal_data: consentString === 'on' || consentString === 'true',
      },
      meta: { source: 'mini_app' },
    };

    const preparedAttachments = attachments
      .map((attachment) => ({
        name: attachment.name.trim(),
        url: attachment.url.trim(),
      }))
      .filter((attachment) => attachment.name && attachment.url);

    if (preparedAttachments.length) {
      payload.attachments = preparedAttachments;
    }

    setInquiryStatus('submitting');
    setError(null);

    try {
      await submitAdmissionInquiry(payload);
      setInquiryStatus('success');
      event.currentTarget.reset();
      setAttachments([{ id: generateAttachmentId(), name: '', url: '' }]);
    } catch (submitError) {
      console.error('Failed to submit admission inquiry', submitError);
      setInquiryStatus('error');
      setError('Не удалось отправить вопрос. Попробуйте снова позже.');
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <form className="card" onSubmit={handleInquirySubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-full-name">
              Полное имя
            </label>
            <input className="form-input" id="inquiry-full-name" name="full_name" placeholder="Иван Иванов" required />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-email">
              Email
            </label>
            <input className="form-input" id="inquiry-email" type="email" name="email" placeholder="student@example.com" required />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-phone">
              Телефон
            </label>
            <input className="form-input" id="inquiry-phone" name="phone" placeholder="+7 900 000-00-00" required />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-topic">
              Тема вопроса
            </label>
            <select className="form-input" id="inquiry-topic" name="topic" required>
              <option value="">Выберите тему</option>
              {ADMISSION_TOPICS.map((topic) => (
                <option key={topic.id} value={topic.id}>
                  {topic.title}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-program">
              Программа (необязательно)
            </label>
            <select className="form-input" id="inquiry-program" name="program_id" defaultValue="">
              <option value="">Выберите программу</option>
              {programs.map((program) => (
                <option key={program.id} value={program.id}>
                  {program.title}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="inquiry-question">
              Вопрос
            </label>
            <textarea className="form-input" id="inquiry-question" name="question" placeholder="Расскажите, пожалуйста, про условия поступления." rows={4} required />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="form-label">Вложения (необязательно)</label>
              <button className="btn btn-secondary btn-small" type="button" onClick={addAttachment}>
                Добавить ссылку
              </button>
            </div>
            <div className="attachment-grid">
              {attachments.map((attachment, index) => (
                <div key={attachment.id} className="attachment-row">
                  <input
                    className="form-input"
                    name={`attachment-name-${attachment.id}`}
                    placeholder="Название файла (например, portfolio.pdf)"
                    value={attachment.name}
                    onChange={(event) => handleAttachmentChange(attachment.id, 'name', event.target.value)}
                  />
                  <input
                    className="form-input"
                    name={`attachment-url-${attachment.id}`}
                    placeholder="https://example.com/portfolio.pdf"
                    value={attachment.url}
                    onChange={(event) => handleAttachmentChange(attachment.id, 'url', event.target.value)}
                  />
                  {attachments.length > 1 ? (
                    <button className="btn btn-secondary btn-icon" type="button" onClick={() => removeAttachment(attachment.id)}>
                      ×
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" id="inquiry-consent" name="consents.personal_data" defaultChecked required />
            <label htmlFor="inquiry-consent" style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Согласен на обработку персональных данных
            </label>
          </div>

          <button className="btn" type="submit" disabled={inquiryStatus === 'submitting'}>
            {inquiryStatus === 'submitting' ? 'Отправляем...' : 'Отправить обращение'}
          </button>
          {inquiryStatus === 'success' ? <div className="card-description">Ваш вопрос отправлен, мы свяжемся с вами в ближайшее время.</div> : null}
          {inquiryStatus === 'error' ? <div className="card-description">{error}</div> : null}
        </form>
      </div>
    </div>
  );
}

