import { Book } from './book';
import { GoogleBookDetails } from './google-book-details';
import { LibraryItem } from './library-item';
import { Review } from './review';

export interface BookOverview {
  book: Book;
  google_details?: GoogleBookDetails | null;
  library_item?: LibraryItem | null;
  review?: Review | null;
}
