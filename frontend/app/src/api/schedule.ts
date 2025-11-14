import { apiFetch } from './httpClient';

export interface ScheduleRange {
  from: string;
  to: string;
  time_zone?: string;
}

export interface ScheduleGroup {
  id: string;
  name?: string;
  faculty?: string;
}

export interface ScheduleRoom {
  name?: string;
  campus?: string;
  building?: string;
}

export interface ScheduleTeacher {
  id?: string;
  full_name?: string;
  email?: string;
}

export interface ScheduleItem {
  id: string;
  subject: string;
  lesson_type?: string;
  starts_at: string;
  ends_at: string;
  format?: string;
  room?: ScheduleRoom;
  teacher?: ScheduleTeacher;
  group_id?: string;
  stream?: string;
  notes?: string;
}

export interface ScheduleResponse {
  range: ScheduleRange;
  group?: ScheduleGroup;
  items: ScheduleItem[];
  meta?: {
    generated_at?: string;
    schedule_version?: string;
    source?: string;
  };
}

export interface ScheduleQuery {
  from: string;
  to: string;
  groupId?: string;
}

export async function getMySchedule({ from, to, groupId }: ScheduleQuery): Promise<ScheduleResponse> {
  const params = new URLSearchParams();
  params.set('from', from);
  params.set('to', to);
  if (groupId) {
    params.set('group_id', groupId);
  }

  return apiFetch<ScheduleResponse>(`/schedule/my?${params.toString()}`);
}

