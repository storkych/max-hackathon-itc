import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import {
  getLibraryBooks,
  getLibraryFines,
  getLibraryHolds,
  submitLibraryFinePayment,
  submitLibraryHold,
  type LibraryBook,
  type LibraryFine,
  type LibraryHold,
} from '../../../api/library';
import { BookOpenCheck, Headphones, Layers, LibrarySquare } from 'lucide-react';

const mediaLabels: Record<string, string> = {
  book: 'Печатная книга',
  ebook: 'Электронная книга',
  audiobook: 'Аудиокнига',
  magazine: 'Журнал',
  article: 'Статья',
};

const mediaIcons: Record<string, JSX.Element> = {
  book: <BookOpenCheck size={16} />,
  ebook: <LibrarySquare size={16} />,
  audiobook: <Headphones size={16} />,
  magazine: <Layers size={16} />,
};

export function LibraryPage() {
  const [books, setBooks] = useState<LibraryBook[]>([]);
  const [holds, setHolds] = useState<LibraryHold[]>([]);
  const [fines, setFines] = useState<LibraryFine[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [mediaFilter, setMediaFilter] = useState<'all' | string>('all');
  const [holdStatus, setHoldStatus] = useState<Record<string, 'idle' | 'submitting' | 'success'>>({});
  const [fineStatus, setFineStatus] = useState<'idle' | 'submitting' | 'success'>('idle');
  const [activeTab, setActiveTab] = useState<'catalog' | 'holds'>('catalog');

  useEffect(() => {
    const load = async () => {
      try {
        const [catalog, holdsData, finesData] = await Promise.all([getLibraryBooks(), getLibraryHolds(), getLibraryFines()]);
        setBooks(Array.isArray(catalog) ? catalog : []);
        setHolds(Array.isArray(holdsData) ? holdsData : []);
        setFines(Array.isArray(finesData) ? finesData : []);
      } catch (error) {
        console.error('Failed to load library data', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredBooks = useMemo(() => {
    return books.filter((book) => {
      const matchesMedia = mediaFilter === 'all' || (book.media_type ?? 'book') === mediaFilter;
      const term = search.trim().toLowerCase();
      if (!term) {
        return matchesMedia;
      }
      const fields = [
        book.title,
        book.subtitle,
        ...(book.authors ?? []),
        book.publisher,
        ...(book.tags ?? []),
        ...(book.categories ?? []),
        book.description,
      ]
        .filter(Boolean)
        .map((value) => value!.toLowerCase());
      const matchesSearch = fields.some((value) => value.includes(term));
      return matchesMedia && matchesSearch;
    });
  }, [books, search, mediaFilter]);

  const handleQuickHold = async (itemId: string) => {
    setHoldStatus((prev) => ({ ...prev, [itemId]: 'submitting' }));
    try {
      await submitLibraryHold(itemId, 'Главная библиотека');
      const holdsData = await getLibraryHolds();
      setHolds(Array.isArray(holdsData) ? holdsData : []);
      setHoldStatus((prev) => ({ ...prev, [itemId]: 'success' }));
    } catch (error) {
      console.error('Failed to submit library hold', error);
      setHoldStatus((prev) => ({ ...prev, [itemId]: 'idle' }));
    }
  };

  const handleFinePayment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const loanId = formData.get('loan_id') as string;
    if (!loanId) return;
    const fine = fines.find((item) => item.id === loanId);
    if (!fine) return;
    setFineStatus('submitting');
    try {
      await submitLibraryFinePayment(loanId, fine.amount, 'RUB');
      const finesData = await getLibraryFines();
      setFines(Array.isArray(finesData) ? finesData : []);
      setFineStatus('success');
      event.currentTarget.reset();
    } catch (error) {
      console.error('Failed to pay library fine', error);
      setFineStatus('idle');
    }
  };

  const FALLBACK_COVER =
    'data:image/svg+xml;charset=UTF-8,' +
    encodeURIComponent(
      `<svg width="120" height="160" xmlns="http://www.w3.org/2000/svg">
        <rect width="120" height="160" rx="12" fill="#E9ECEF"/>
        <text x="50%" y="50%" text-anchor="middle" fill="#ADB5BD" font-family="Arial" font-size="14">MAX</text>
      </svg>`,
    );

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Библиотека</h1>
            <p className="subtitle">Каталог изданий, аудиокниг и журналов кампуса</p>
          </div>
        </div>

        <div className="library-tabs">
          <button
            type="button"
            className={`library-tab${activeTab === 'catalog' ? ' library-tab--active' : ''}`}
            onClick={() => setActiveTab('catalog')}
          >
            Каталог
          </button>
          <button
            type="button"
            className={`library-tab${activeTab === 'holds' ? ' library-tab--active' : ''}`}
            onClick={() => setActiveTab('holds')}
          >
            Бронирование
          </button>
        </div>

        {activeTab === 'catalog' ? (
          <>
            <div className="library-toolbar">
              <input
                className="form-input"
                type="search"
                placeholder="Поиск по названию, автору или тегу"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                disabled={loading}
              />
              <select
                className="form-input"
                value={mediaFilter}
                onChange={(event) => setMediaFilter(event.target.value)}
                disabled={loading}
              >
                <option value="all">Все форматы</option>
                <option value="book">Печатные книги</option>
                <option value="ebook">Электронные книги</option>
                <option value="audiobook">Аудиокниги</option>
                <option value="magazine">Журналы</option>
              </select>
            </div>

            {loading ? (
              <div className="library-card-grid">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={`library-skeleton-${index}`} className="card library-card library-card--skeleton">
                    <div className="library-cover skeleton-block" />
                    <div className="library-card-body">
                      <div className="library-card-header">
                        <span className="skeleton-line" style={{ width: '30%' }} />
                        <span className="skeleton-pill" />
                      </div>
                      <div className="skeleton-line" style={{ width: '80%' }} />
                      <div className="skeleton-line" style={{ width: '60%' }} />
                      <div className="skeleton-line" style={{ width: '70%' }} />
                      <div className="skeleton-line" style={{ width: '55%' }} />
                      <div className="skeleton-chip-row">
                        <span className="skeleton-chip" />
                        <span className="skeleton-chip" />
                        <span className="skeleton-chip" />
                      </div>
                      <div className="skeleton-button" />
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredBooks.length === 0 ? (
              <div className="card-description">По вашему запросу ничего не найдено.</div>
            ) : (
              <div className="library-card-grid">
                {filteredBooks.map((book) => {
                  const mediaType = book.media_type ?? 'book';
                  const availabilityLabel =
                    typeof book.availability?.in_stock === 'number'
                      ? `${book.availability.in_stock} в наличии`
                      : 'Доступность уточняется';
                  const coverSrc =
                    book.cover_url && !book.cover_url.includes('example.com') ? book.cover_url : FALLBACK_COVER;
                  return (
                    <div key={book.id} className="card library-card">
                      <div className="library-cover">
                        <img
                          src={coverSrc}
                          alt={book.title}
                          loading="lazy"
                          onError={(event) => {
                            event.currentTarget.onerror = null;
                            event.currentTarget.src = FALLBACK_COVER;
                          }}
                        />
                      </div>
                      <div className="library-card-body">
                        <div className="library-card-header">
                          <span className="library-media">
                            {mediaIcons[mediaType] ?? <BookOpenCheck size={16} />}
                            {mediaLabels[mediaType] ?? 'Издание'}
                          </span>
                          <span className={`library-availability${book.availability?.in_stock ? ' library-availability--in-stock' : ''}`}>
                            {availabilityLabel}
                          </span>
                        </div>
                        <h2>{book.title}</h2>
                        {book.subtitle && <p className="library-subtitle">{book.subtitle}</p>}
                        {book.authors && book.authors.length > 0 && <div className="library-meta-line">Автор(ы): {book.authors.join(', ')}</div>}
                        {book.publisher && (
                          <div className="library-meta-line">
                            Издатель: {book.publisher} {book.published_year ? `· ${book.published_year}` : ''}
                          </div>
                        )}
                        {book.description && <p className="library-description">{book.description}</p>}
                        <div className="library-chip-row">
                          {book.tags?.map((tag) => (
                            <span key={`${book.id}-${tag}`} className="library-chip">
                              {tag}
                            </span>
                          ))}
                          {book.categories?.map((category) => (
                            <span key={`${book.id}-${category}`} className="library-chip library-chip--ghost">
                              {category}
                            </span>
                          ))}
                          {book.language && <span className="library-chip">{book.language.toUpperCase()}</span>}
                        </div>
                        <button
                          className="btn btn-secondary library-hold-btn"
                          type="button"
                          disabled={holdStatus[book.id] === 'submitting'}
                          onClick={() => handleQuickHold(book.id)}
                        >
                          {holdStatus[book.id] === 'success'
                            ? 'Заявка отправлена'
                            : holdStatus[book.id] === 'submitting'
                              ? 'Отправляем...'
                              : 'Забронировать'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        ) : (
          <div className="library-hold-layout">
            <div className="card library-card-list">
              <div className="card-title">Мои брони</div>
              {loading ? (
                <div className="library-card-stack">
                  {Array.from({ length: 2 }).map((_, index) => (
                    <div key={`hold-skeleton-${index}`} className="library-hold-card">
                      <div className="skeleton-line" style={{ width: '70%' }} />
                      <div className="skeleton-line" style={{ width: '40%' }} />
                    </div>
                  ))}
                </div>
              ) : holds.length === 0 ? (
                <div className="card-description">Броней пока нет.</div>
              ) : (
                <div className="library-card-stack">
                  {holds.map((hold) => (
                    <div key={hold.id} className="library-hold-card">
                      <strong>{hold.item_title ?? hold.item_id}</strong>
                      <span>{hold.status === 'ready' ? 'Готово к выдаче' : hold.status === 'queued' ? 'В очереди' : 'В обработке'}</span>
                      {typeof hold.position === 'number' && <span>Позиция в очереди: {hold.position}</span>}
                      {hold.pickup_location && <span>Пункт выдачи: {hold.pickup_location}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {!loading && fines.length > 0 && (
              <form className="card library-form" onSubmit={handleFinePayment}>
                <div className="card-title">Оплатить штраф</div>
                <div className="form-group">
                  <label className="form-label" htmlFor="fine-loan">
                    Выберите штраф
                  </label>
                  <select className="form-input" id="fine-loan" name="loan_id" required>
                    <option value="">Выберите задолженность</option>
                    {fines.map((fine) => (
                      <option key={fine.id} value={fine.id}>
                        {fine.id} · {fine.amount.toLocaleString('ru-RU')} ₽
                      </option>
                    ))}
                  </select>
                </div>
                <button className="btn" type="submit" disabled={fineStatus === 'submitting'}>
                  {fineStatus === 'submitting' ? 'Оплачиваем...' : 'Оплатить штраф'}
                </button>
                {fineStatus === 'success' && <div className="card-description">Оплата проведена. Спасибо!</div>}
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

