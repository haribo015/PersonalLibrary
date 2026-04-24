export interface GoogleBookDetails {
  subtitle?: string | null;
  publisher?: string | null;
  page_count?: number | null;
  categories: string[];
  language?: string | null;
  average_rating?: number | null;
  ratings_count?: number | null;
  preview_link?: string | null;
  info_link?: string | null;
  maturity_rating?: string | null;
}
