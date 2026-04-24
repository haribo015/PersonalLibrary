import { Book } from './book';

export interface ReviewPayload {
  book_id: number;
  rating: number;
  comment?: string;
}

export interface Review {
  id: number;
  user_id: number;
  book_id: number;
  rating: number;
  comment?: string;
  created_at: string;
  book: Book;
}
