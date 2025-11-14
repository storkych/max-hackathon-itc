import { apiFetch } from './httpClient';

type ApiListResponse<T> = {
  data?: T[];
  items?: T[];
  results?: T[];
};

function extractList<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload && typeof payload === 'object') {
    const objectPayload = payload as ApiListResponse<T>;
    if (Array.isArray(objectPayload.results)) {
      return objectPayload.results;
    }
    if (Array.isArray(objectPayload.items)) {
      return objectPayload.items;
    }
    if (Array.isArray(objectPayload.data)) {
      return objectPayload.data;
    }
  }
  return [];
}

const generateId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `hr-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export interface TravelRequest {
  id: string;
  title: string;
  purpose?: string;
  destination?: {
    city?: string;
    country?: string;
  };
  startDate: string;
  endDate: string;
  status?: string;
}

export interface LeaveRequest {
  id: string;
  type?: string;
  startDate: string;
  endDate: string;
  status?: string;
  replacement?: {
    fullName?: string;
    contacts?: string;
  };
}

export interface GuestPass {
  id: string;
  guestFullName: string;
  guestCompany?: string;
  visitDate: string;
  visitTimeFrom?: string;
  visitTimeTo?: string;
  notes?: string;
  status?: string;
}

export interface TravelRequestPayload {
  title: string;
  purpose: string;
  destination: {
    city: string;
    country?: string;
  };
  start_date: string;
  end_date: string;
  transport?: {
    type?: string;
    class?: string;
  };
  accommodations?: Array<{
    hotel?: string;
    check_in?: string;
    check_out?: string;
  }>;
  expenses_plan?: Array<{
    category?: string;
    amount?: number;
    currency?: string;
  }>;
}

export interface LeaveRequestPayload {
  leave_type: string;
  start_date: string;
  end_date: string;
  replacement?: {
    full_name?: string;
    contacts?: string;
  };
}

export interface GuestPassPayload {
  guest_full_name: string;
  guest_company?: string;
  visit_date: string;
  visit_time_from: string;
  visit_time_to: string;
  notes?: string;
}

function mapTravelRequest(raw: any): TravelRequest {
  return {
    id: raw?.id ?? raw?.request_id ?? generateId(),
    title: raw?.title ?? 'Командировка',
    purpose: raw?.purpose ?? raw?.goal ?? undefined,
    destination: raw?.destination
      ? {
          city: raw.destination.city ?? raw.destination_city,
          country: raw.destination.country ?? raw.destination_country,
        }
      : undefined,
    startDate: raw?.start_date ?? raw?.startDate ?? '',
    endDate: raw?.end_date ?? raw?.endDate ?? '',
    status: raw?.status,
  };
}

function mapLeaveRequest(raw: any): LeaveRequest {
  return {
    id: raw?.id ?? raw?.request_id ?? generateId(),
    type: raw?.leave_type ?? raw?.type,
    startDate: raw?.start_date ?? raw?.startDate ?? '',
    endDate: raw?.end_date ?? raw?.endDate ?? '',
    status: raw?.status,
    replacement: raw?.replacement
      ? {
          fullName: raw.replacement.full_name ?? raw.replacement.fullName,
          contacts: raw.replacement.contacts ?? raw.replacement.contact,
        }
      : undefined,
  };
}

function mapGuestPass(raw: any): GuestPass {
  return {
    id: raw?.id ?? generateId(),
    guestFullName: raw?.guest_full_name ?? raw?.guestFullName ?? 'Гость',
    guestCompany: raw?.guest_company ?? raw?.guestCompany,
    visitDate: raw?.visit_date ?? raw?.visitDate ?? '',
    visitTimeFrom: raw?.visit_time_from ?? raw?.visitTimeFrom,
    visitTimeTo: raw?.visit_time_to ?? raw?.visitTimeTo,
    notes: raw?.notes,
    status: raw?.status,
  };
}

export async function getMyTravelRequests(): Promise<TravelRequest[]> {
  const response = await apiFetch(`/hr/travel/requests/my`);
  return extractList(response).map(mapTravelRequest);
}

export async function submitTravelRequest(payload: TravelRequestPayload) {
  await apiFetch('/hr/travel/requests', {
    method: 'POST',
    body: payload,
  });
}

export async function getMyLeaveRequests(): Promise<LeaveRequest[]> {
  const response = await apiFetch(`/hr/leave/requests/my`);
  return extractList(response).map(mapLeaveRequest);
}

export async function submitLeaveRequest(payload: LeaveRequestPayload) {
  await apiFetch('/hr/leave/requests', {
    method: 'POST',
    body: payload,
  });
}

export async function getMyGuestPasses(): Promise<GuestPass[]> {
  const response = await apiFetch(`/office/guest-passes/my`);
  return extractList(response).map(mapGuestPass);
}

export async function submitGuestPass(payload: GuestPassPayload) {
  await apiFetch('/office/guest-passes', {
    method: 'POST',
    body: payload,
  });
}

