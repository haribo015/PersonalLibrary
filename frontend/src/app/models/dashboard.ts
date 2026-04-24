export interface DashboardMetric {
  label: string;
  value: number;
}

export interface DashboardOverview {
  books_in_library: number;
  books_read_this_year: number;
  books_in_progress: number;
  books_to_read: number;
  books_dnf: number;
  favorite_books: number;
  completion_rate: number;
  average_rating: number;
  reading_goal: number;
  reading_goal_progress: number;
  categories: DashboardMetric[];
  formats: DashboardMetric[];
  statuses: DashboardMetric[];
  priorities: DashboardMetric[];
  top_tags: DashboardMetric[];
}
