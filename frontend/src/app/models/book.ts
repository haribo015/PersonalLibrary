// Mirrors the backend BookPayload plus UI hints returned by search endpoints.
export interface Book {
  id?: number;
  google_book_id: string;
  title: string;
  authors?: string;
  description?: string;
  cover_image?: string;
  published_date?: string;
  already_in_library?: boolean;
}
