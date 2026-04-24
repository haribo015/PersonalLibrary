import { Book } from './book';

export interface LibraryItem {
  id: number;
  user_id: number;
  book_id: number;
  category: string;
  reading_status: string;
  priority: string;
  source: string;
  reading_format: string;
  pages_total?: number;
  pages_read?: number;
  started_at?: string;
  finished_at?: string;
  last_opened_at?: string;
  personal_notes?: string;
  favorite: boolean;
  tags?: string;
  created_at: string;
  book: Book;
}
