import type { ReactNode } from 'react';
import {
  BookOpen,
  FileText,
  Calendar,
  MapPin,
  HelpCircle,
  MessageSquare,
  Rocket,
  ClipboardList,
  CheckSquare,
  Briefcase,
  Search,
  Home,
  PartyPopper,
  Library,
  Plane,
  Umbrella,
  Building,
  BarChart3,
  TrendingUp,
  Newspaper,
  Settings,
  LayoutDashboard,
  DoorOpen,
} from 'lucide-react';

interface IconProps {
  className?: string;
  size?: number;
}

const iconSize = 24;

// Маппинг иконок по ID секций
const iconMap: Record<string, (props: IconProps) => ReactNode> = {
  'home': (props) => <Home {...props} size={props.size || iconSize} />,
  'university-info': (props) => <LayoutDashboard {...props} size={props.size || iconSize} />,
  'programs': (props) => <BookOpen {...props} size={props.size || iconSize} />,
  'admission-conditions': (props) => <FileText {...props} size={props.size || iconSize} />,
  'open-day': (props) => <DoorOpen {...props} size={props.size || iconSize} />,
  'excursion': (props) => <MapPin {...props} size={props.size || iconSize} />,
  'admission-inquiry': (props) => <HelpCircle {...props} size={props.size || iconSize} />,
  'schedule': (props) => <Calendar {...props} size={props.size || iconSize} />,
  'feedback': (props) => <MessageSquare {...props} size={props.size || iconSize} />,
  'electives': (props) => <BookOpen {...props} size={props.size || iconSize} />,
  'free-classrooms': (props) => <Building {...props} size={props.size || iconSize} />,
  'projects': (props) => <Rocket {...props} size={props.size || iconSize} />,
  'available-projects': (props) => <ClipboardList {...props} size={props.size || iconSize} />,
  'task-tracker': (props) => <CheckSquare {...props} size={props.size || iconSize} />,
  'career': (props) => <Briefcase {...props} size={props.size || iconSize} />,
  'vacancies': (props) => <Search {...props} size={props.size || iconSize} />,
  'deanery': (props) => <FileText {...props} size={props.size || iconSize} />,
  'dormitory': (props) => <Home {...props} size={props.size || iconSize} />,
  'events': (props) => <PartyPopper {...props} size={props.size || iconSize} />,
  'library': (props) => <Library {...props} size={props.size || iconSize} />,
  'business-trips': (props) => <Plane {...props} size={props.size || iconSize} />,
  'vacations': (props) => <Umbrella {...props} size={props.size || iconSize} />,
  'office': (props) => <Settings {...props} size={props.size || iconSize} />,
  'campus-management': (props) => <BarChart3 {...props} size={props.size || iconSize} />,
  'academic-metrics': (props) => <TrendingUp {...props} size={props.size || iconSize} />,
  'news-aggregator': (props) => <Newspaper {...props} size={props.size || iconSize} />,
};

export function getIcon(iconId: string | undefined, className?: string): ReactNode {
  if (!iconId) {
    return null;
  }
  const IconComponent = iconMap[iconId];
  if (!IconComponent) {
    return null;
  }
  return <IconComponent className={className} />;
}
