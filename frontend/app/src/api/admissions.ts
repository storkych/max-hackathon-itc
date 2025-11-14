import { apiFetch, ApiError } from './httpClient';

export interface UniversityContacts {
  address?: string;
  phone?: string;
  email?: string;
  site?: string;
}

export interface UniversityMedia {
  imageUrl?: string;
  logoUrl?: string;
}

export interface UniversityFeatures {
  hasDormitory?: boolean;
  hasMilitaryDepartment?: boolean;
  hasOpenDay?: boolean;
  hasPreparatoryCourses?: boolean;
  hasDistancePrograms?: boolean;
}

export interface UniversityStats {
  studentsTotal?: number;
  programsCount?: number;
  budgetQuota?: number;
  employmentRate?: number;
}

export interface AdmissionsUniversity {
  id: string;
  name: string;
  shortTitle?: string;
  title?: string;
  city?: string;
  region?: string;
  about?: string;
  description?: string;
  rating?: string;
  hasDormitory?: boolean;
  contacts?: UniversityContacts;
  media?: UniversityMedia;
  features?: UniversityFeatures;
  stats?: UniversityStats;
  lastUpdated?: string;
  meta?: Record<string, unknown>;
}

export interface AdmissionsProgramDepartment {
  id: string;
  title: string;
}

export interface AdmissionsProgramLinks {
  landing?: string;
  syllabus?: string;
}

export interface AdmissionsProgramMedia {
  coverUrl?: string;
}

export interface AdmissionsProgram {
  id: string;
  universityId?: string;
  title: string;
  level?: string;
  format?: string;
  description?: string;
  language?: string;
  duration?: string;
  durationYears?: number;
  tuition?: string;
  tuitionPerYear?: string;
  hasBudget?: boolean;
  budgetSeats?: number;
  paidSeats?: number;
  targetedSeats?: number;
  passingScore?: number;
  admissionDeadline?: string;
  exams?: string[];
  features?: string[];
  careerPaths?: string[];
  department?: AdmissionsProgramDepartment;
  links?: AdmissionsProgramLinks;
  media?: AdmissionsProgramMedia;
}

export interface AdmissionsProgramFilters {
  departments: AdmissionsProgramDepartment[];
  levels: string[];
  formats: string[];
}

export interface AdmissionsProgramsResult {
  programs: AdmissionsProgram[];
  filters: AdmissionsProgramFilters;
}

export interface ProgramRequirement {
  programId: string;
  year?: number;
  minScore?: number;
  minScorePaid?: number;
  subjects: Array<{ subject: string; minScore: number }>;
  specialConditions: string[];
  documents: string[];
  deadlines?: { exams?: string; documents?: string };
  applicationPortal?: string;
  benefits?: string[];
}

export interface OpenDayEvent {
  id: string;
  title?: string;
  date: string;
  time?: string;
  startsAt?: string;
  endsAt?: string;
  type?: string;
  city?: string;
  format?: string;
  speakers?: string[];
  capacity?: number;
  registered?: number;
  remaining?: number;
  location?: string;
  description?: string;
  media?: { posterUrl?: string };
  registrationLink?: string;
  registrationDeadline?: string;
  registrationOpen?: boolean;
  contacts?: { email?: string; phone?: string };
  programs?: Array<{ id: string; title: string }>;
}

export interface OpenDayFilters {
  cities: string[];
  types: string[];
}

export interface OpenDayResult {
  events: OpenDayEvent[];
  filters: OpenDayFilters;
}

type ApiListResponse<T> = { data?: T[]; items?: T[] };
type ApiSingleResponse<T> = { data?: T };

function unwrapList<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }

  if (typeof payload === 'object' && payload !== null) {
    const objectPayload = payload as ApiListResponse<T>;
    if (Array.isArray(objectPayload.data)) {
      return objectPayload.data;
    }
    if (Array.isArray(objectPayload.items)) {
      return objectPayload.items;
    }
  }

  return [];
}

function unwrapSingle<T>(payload: unknown): T | null {
  if (!payload) {
    return null;
  }

  if (typeof payload === 'object' && payload !== null) {
    const objectPayload = payload as ApiSingleResponse<T>;
    if (objectPayload.data) {
      return objectPayload.data;
    }
  }

  return payload as T;
}

function mapUniversity(raw: any): AdmissionsUniversity {
  return {
    id: raw?.id ?? raw?.uuid ?? '',
    name: raw?.name ?? raw?.title ?? 'Неизвестный вуз',
    shortTitle: raw?.short_title ?? raw?.shortTitle,
    title: raw?.title ?? raw?.name,
    city: raw?.city ?? raw?.location?.city,
    region: raw?.region ?? raw?.location?.region,
    about: raw?.about,
    description: raw?.description ?? raw?.about ?? '',
    rating: raw?.rating?.toString() ?? raw?.rank?.toString(),
    contacts: raw?.contacts
      ? {
          address: raw.contacts.address ?? raw.contacts.location,
          phone: raw.contacts.phone,
          email: raw.contacts.email,
          site: raw.contacts.site ?? raw.contacts.website,
        }
      : undefined,
    media: raw?.media
      ? {
          imageUrl: raw.media.image_url ?? raw.media.cover_url,
          logoUrl: raw.media.logo_url ?? raw.media.icon_url,
        }
      : undefined,
    hasDormitory: raw?.features?.has_dormitory ?? raw?.has_dormitory ?? raw?.hasDormitory,
    features: {
      hasDormitory: raw?.features?.has_dormitory ?? raw?.has_dormitory ?? raw?.hasDormitory,
      hasMilitaryDepartment: raw?.features?.has_military_department ?? raw?.has_military_department,
      hasOpenDay: raw?.features?.has_open_day ?? raw?.has_open_day,
      hasPreparatoryCourses: raw?.features?.has_preparatory_courses ?? raw?.has_preparatory_courses,
      hasDistancePrograms: raw?.features?.has_distance_programs ?? raw?.has_distance_programs,
    },
    stats: raw?.stats
      ? {
          studentsTotal: raw.stats.students_total ?? raw.stats.studentsTotal,
          programsCount: raw.stats.programs_count ?? raw.stats.programsCount,
          budgetQuota: raw.stats.budget_quota ?? raw.stats.budgetQuota,
          employmentRate: raw.stats.employment_rate ?? raw.stats.employmentRate,
        }
      : undefined,
    lastUpdated: raw?.last_updated ?? raw?.meta?.last_updated,
    meta: raw?.meta,
  };
}

function mapProgram(raw: any): AdmissionsProgram {
  return {
    id: raw?.id ?? raw?.program_id ?? '',
    universityId: raw?.university_id ?? raw?.universityId,
    title: raw?.title ?? raw?.name ?? 'Программа',
    level: raw?.level ?? raw?.education_level ?? undefined,
    format: raw?.format ?? raw?.study_format ?? undefined,
    description: raw?.description ?? raw?.summary,
    language: raw?.language,
    duration: raw?.duration ?? raw?.study_duration ?? (raw?.duration_years ? `${raw.duration_years} года` : undefined),
    durationYears: raw?.duration_years ?? raw?.durationYears,
    tuition: raw?.tuition ?? raw?.tuition_fee ?? raw?.tuition_per_year,
    tuitionPerYear: raw?.tuition_per_year ?? raw?.tuitionPerYear ?? raw?.tuition_fee,
    hasBudget: raw?.has_budget ?? raw?.hasBudget,
    budgetSeats: raw?.budget_seats ?? raw?.budgetSeats ?? raw?.budget_places,
    paidSeats: raw?.paid_places ?? raw?.paidSeats,
    targetedSeats: raw?.targeted_places ?? raw?.targetedSeats,
    passingScore: raw?.passing_score_last_year ?? raw?.passingScore,
    admissionDeadline: raw?.admission_deadline ?? raw?.deadline,
    exams: raw?.exams ?? raw?.entrance_exams ?? [],
    features: raw?.features ?? raw?.highlights ?? [],
    careerPaths: raw?.career_paths ?? raw?.careerPaths ?? [],
    department: raw?.department
      ? {
          id: raw.department.id ?? '',
          title: raw.department.title ?? raw.department.name ?? 'Кафедра',
        }
      : undefined,
    links: raw?.links ?? undefined,
    media: raw?.media
      ? {
          coverUrl: raw.media.cover_url ?? raw.media.image_url,
        }
      : undefined,
  };
}

const BENEFIT_LABELS: Record<string, string> = {
  olympiad: 'Олимпиады',
  scholarship: 'Стипендии',
  internship: 'Стажировки',
  mentoring: 'Наставничество',
};

function formatBenefitKey(key: string) {
  if (BENEFIT_LABELS[key]) {
    return BENEFIT_LABELS[key];
  }
  return key
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function mapRequirement(raw: any): ProgramRequirement {
  const examsSource = Array.isArray(raw?.exams) ? raw.exams : raw?.subjects ?? [];
  const documentsSource = Array.isArray(raw?.documents) ? raw.documents : [];
  const specialSource = Array.isArray(raw?.special_conditions) ? raw.special_conditions : raw?.specialConditions ?? [];
  const assembledSpecial: string[] = specialSource.map((entry: any) =>
    typeof entry === 'string' ? entry : entry?.title ?? entry?.name ?? 'Дополнительное условие',
  );

  if (raw?.benefits && typeof raw.benefits === 'object') {
    Object.entries(raw.benefits).forEach(([key, value]) => {
      if (value) {
        assembledSpecial.push(`${formatBenefitKey(key)} — ${value}`);
      }
    });
  }
  if (Array.isArray(raw?.additional_tests)) {
    raw.additional_tests.forEach((test: any) => {
      if (test) {
        assembledSpecial.push(typeof test === 'string' ? test : test?.title ?? 'Дополнительный тест');
      }
    });
  }

  const documents = documentsSource.map((document: any) => {
    if (typeof document === 'string') {
      return document;
    }
    const title = document?.title ?? document?.name ?? 'Документ';
    const description = document?.description ?? document?.details;
    return description ? `${title} — ${description}` : title;
  });

  return {
    programId: raw?.program?.id ?? raw?.program_id ?? raw?.programId ?? '',
    year: raw?.campaign?.year ?? raw?.year ?? undefined,
    minScore: raw?.thresholds?.budget ?? raw?.min_score ?? raw?.minScore ?? undefined,
    minScorePaid: raw?.thresholds?.paid ?? undefined,
    subjects: examsSource.map((subject: any) => ({
      subject: subject?.subject ?? subject?.title ?? subject?.name ?? 'Предмет',
      minScore: subject?.min_score ?? subject?.minScore ?? subject?.threshold ?? 0,
    })),
    specialConditions: assembledSpecial,
    documents,
    deadlines: raw?.deadlines,
    applicationPortal: raw?.application?.portal,
    benefits:
      raw?.benefits && typeof raw.benefits === 'object'
        ? Object.entries(raw.benefits).map(([key, value]) => `${key}: ${value}`)
        : undefined,
  };
}

function mapOpenDay(raw: any): OpenDayEvent {
  return {
    id: raw?.id ?? raw?.event_id ?? '',
    title: raw?.title,
    date: raw?.date ?? raw?.start_date ?? new Date().toISOString(),
    time: raw?.time ?? raw?.start_time ?? undefined,
    startsAt: raw?.starts_at,
    endsAt: raw?.ends_at,
    type: raw?.type,
    city: raw?.city,
    format: raw?.format ?? raw?.type ?? undefined,
    speakers: raw?.speakers ?? raw?.hosts ?? [],
    capacity: raw?.capacity ?? raw?.max_participants ?? undefined,
    registered: raw?.registered ?? raw?.current_participants ?? undefined,
    remaining: raw?.remaining,
    location: raw?.location,
    description: raw?.description,
    media: raw?.media
      ? {
          posterUrl: raw.media.poster_url ?? raw.media.image_url,
        }
      : undefined,
    registrationLink: raw?.links?.registration ?? raw?.registration_link,
    registrationDeadline: raw?.registration_deadline,
    registrationOpen: raw?.registration_open,
    contacts: raw?.contacts,
    programs: Array.isArray(raw?.programs)
      ? raw.programs.map((program: any) => ({
          id: program?.id ?? '',
          title: program?.title ?? 'Программа',
        }))
      : undefined,
  };
}

function normalizeFilterStrings(source: unknown): string[] {
  if (!Array.isArray(source)) {
    return [];
  }
  const stringItems = source.filter((item): item is string => typeof item === 'string' && item.trim().length > 0);
  return Array.from(new Set(stringItems));
}

export async function getAdmissionsUniversities(): Promise<AdmissionsUniversity[]> {
  const response = await apiFetch<ApiListResponse<any>>('/admissions/universities');
  const items = unwrapList(response);
  return items.map(mapUniversity);
}

export async function getAdmissionsUniversityById(id: string): Promise<AdmissionsUniversity | null> {
  const response = await apiFetch<ApiSingleResponse<any>>(`/admissions/universities/${id}`);
  const item = unwrapSingle(response);
  if (!item) {
    return null;
  }
  return mapUniversity(item);
}

export async function getAdmissionsPrograms(universityId?: string): Promise<AdmissionsProgramsResult> {
  const params = new URLSearchParams();
  if (universityId) {
    params.set('university_id', universityId);
  }
  const query = params.toString();
  const response = await apiFetch<ApiListResponse<any> & { items?: any[]; filters?: any }>(
    `/admissions/programs${query ? `?${query}` : ''}`,
  );
  const items = Array.isArray(response?.items) ? response.items : unwrapList(response);
  const filtersPayload = response?.filters ?? {};

  const departmentsRaw = Array.isArray(filtersPayload.departments) ? filtersPayload.departments : [];
  const departmentsMap = new Map<string, AdmissionsProgramDepartment>();
  departmentsRaw.forEach((dept: any) => {
    const id = dept?.id ?? dept?.code ?? dept?.title ?? '';
    if (!departmentsMap.has(id)) {
      departmentsMap.set(id, {
        id,
        title: dept?.title ?? dept?.name ?? 'Кафедра',
      });
    }
  });

  const levelSet = new Set<string>();
  (Array.isArray(filtersPayload.levels) ? filtersPayload.levels : []).forEach((item: any) => {
    if (typeof item === 'string' && item.trim()) {
      levelSet.add(item);
    }
  });

  const formatSet = new Set<string>();
  (Array.isArray(filtersPayload.formats) ? filtersPayload.formats : []).forEach((item: any) => {
    if (typeof item === 'string' && item.trim()) {
      formatSet.add(item);
    }
  });

  const filters: AdmissionsProgramFilters = {
    departments: Array.from(departmentsMap.values()),
    levels: Array.from(levelSet),
    formats: Array.from(formatSet),
  };

  return {
    programs: items.map(mapProgram),
    filters,
  };
}

export async function getProgramRequirements(programId: string): Promise<ProgramRequirement | null> {
  const params = new URLSearchParams({ program_id: programId });
  const response = await apiFetch<ApiListResponse<any> & { results?: any[] }>(`/admissions/requirements?${params.toString()}`);

  let item: any = null;
  const list = unwrapList(response);
  if (list.length) {
    [item] = list;
  } else if (Array.isArray(response?.results) && response.results.length) {
    [item] = response.results;
  } else if (response && typeof response === 'object') {
    item = response;
  }

  if (!item) {
    return null;
  }
  return mapRequirement(item);
}

export async function getOpenDays(universityId?: string, programId?: string): Promise<OpenDayResult> {
  const params = new URLSearchParams();
  if (universityId) {
    params.set('university_id', universityId);
  }
  if (programId) {
    params.set('program_id', programId);
  }
  const query = params.toString();
  const response = await apiFetch<ApiListResponse<any> & { items?: any[]; filters?: any }>(
    `/admissions/open-days${query ? `?${query}` : ''}`,
  );
  const items = Array.isArray(response?.items) ? response.items : unwrapList(response);
  const filtersPayload = response?.filters ?? {};
  const cities = normalizeFilterStrings(filtersPayload.cities);
  const types = normalizeFilterStrings(filtersPayload.types);
  return {
    events: items.map(mapOpenDay),
    filters: { cities, types },
  };
}

function buildIdempotencyKey() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `idemp-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export async function submitOpenDayRegistration(payload: Record<string, unknown>) {
  try {
    await apiFetch('/admissions/open-days/registrations', {
      method: 'POST',
      headers: {
        'Idempotency-Key': buildIdempotencyKey(),
      },
      body: payload,
    });
    return { success: true };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to submit open day registration', error);
  }
}

export async function submitAdmissionInquiry(payload: Record<string, unknown>) {
  try {
    await apiFetch('/admissions/inquiries', {
      method: 'POST',
      headers: {
        'Idempotency-Key': buildIdempotencyKey(),
      },
      body: payload,
    });
    return { success: true };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to submit admission inquiry', error);
  }
}
