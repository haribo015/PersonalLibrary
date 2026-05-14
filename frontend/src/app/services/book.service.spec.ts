import { of } from 'rxjs';

import { Book } from '../models';
import { ApiService } from './api.service';
import { BookService } from './book.service';

describe('BookService', () => {
  let api: jasmine.SpyObj<ApiService>;
  let service: BookService;

  const book: Book = {
    google_book_id: 'google-1',
    title: 'Clean Code',
    authors: 'Robert C. Martin',
    description: 'Software craftsmanship',
    cover_image: 'cover.jpg',
    published_date: '2008',
    already_in_library: true,
  };

  beforeEach(() => {
    sessionStorage.clear();
    api = jasmine.createSpyObj<ApiService>('ApiService', ['get', 'post', 'delete', 'patch']);
    service = new BookService(api);
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  it('encodes search queries before calling the API', () => {
    api.get.and.returnValue(of([]));

    service.searchBooks('clean code & tests').subscribe();

    expect(api.get).toHaveBeenCalledWith('/books/search?q=clean%20code%20%26%20tests');
  });

  it('sends only API-owned fields when adding a book to the library', () => {
    api.post.and.returnValue(of({} as never));

    service.addToLibrary(book).subscribe();

    expect(api.post).toHaveBeenCalledWith('/library/', {
      google_book_id: 'google-1',
      title: 'Clean Code',
      authors: 'Robert C. Martin',
      description: 'Software craftsmanship',
      cover_image: 'cover.jpg',
      published_date: '2008',
    });
  });

  it('stores navigation context in the session', () => {
    service.setSelectedBook(book);
    service.setLastSearchQuery('clean code');

    expect(service.getSelectedBook()).toEqual(book);
    expect(service.getLastSearchQuery()).toBe('clean code');
  });
});
