import { Book } from './book';

// Payload used when creating or updating the current user's review.
export interface ReviewPayload {
  book_id: number;
  rating: number;
  comment?: string;
}

// Review response includes the book to avoid extra API calls on review screens.
export interface Review {
  id: number;
  user_id: number;
  book_id: number;
  rating: number;
  comment?: string;
  created_at: string;
  book: Book;
}
