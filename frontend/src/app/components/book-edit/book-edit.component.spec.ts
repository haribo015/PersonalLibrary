import { of, throwError } from 'rxjs';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { LibraryItem, Review } from '../../models';
import { BookService } from '../../services/book.service';
import { BookEditComponent } from './book-edit.component';

describe('BookEditComponent', () => {
  let bookService: jasmine.SpyObj<BookService>;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let route: jasmine.SpyObj<ActivatedRoute>;
  let component: BookEditComponent;

  const mockLibraryItem: LibraryItem = {
    id: 1,
    user_id: 1,
    book_id: 1,
    reading_status: 'reading',
    priority: 'high',
    category: 'Roman',
    source: 'user',
    reading_format: 'paper',
    pages_total: 300,
    pages_read: 100,
    started_at: '2024-01-01',
    finished_at: undefined,
    last_opened_at: '2024-06-10',
    personal_notes: 'Good book',
    favorite: true,
    tags: 'fiction',
    created_at: '2024-01-01T10:00:00Z',
    book: {
      id: 1,
      google_book_id: 'abc123',
      title: 'Test Book',
      authors: 'Test Author',
      description: '',
      cover_image: '',
      published_date: '2024-01-01',
    },
  };

  beforeEach(() => {
    const paramMapMock: Partial<ParamMap> = { get: () => '1' };
    bookService = jasmine.createSpyObj<BookService>('BookService', ['getLibrary', 'getReviews', 'updateLibraryItem', 'upsertReview']);
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate', 'getCurrentNavigation']);
    route = {
    snapshot: {
        paramMap: paramMapMock
    }
    } as any as jasmine.SpyObj<ActivatedRoute>;

    router.getCurrentNavigation.and.returnValue(null);
    component = new BookEditComponent(route, router, bookService, auth);
  });

  it('redirects anonymous users to login', () => {
    auth.isLoggedIn.and.returnValue(false);

    component.ngOnInit();

    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('loads library items and reviews when user is authenticated', () => {
    const mockReview: Review = {
      id: 1,
      user_id: 1,
      book_id: 1,
      rating: 4,
      comment: 'Great',
      created_at: '2024-01-01T10:00:00Z',
      book: mockLibraryItem.book,
    };
    auth.isLoggedIn.and.returnValue(true);
    bookService.getLibrary.and.returnValue(of([mockLibraryItem]));
    bookService.getReviews.and.returnValue(of([mockReview]));

    component.ngOnInit();

    expect(bookService.getLibrary).toHaveBeenCalled();
    expect(bookService.getReviews).toHaveBeenCalled();
    expect(component.loading).toBe(false);
  });

  it('displays error when book is not found in library', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.getLibrary.and.returnValue(of([]));
    bookService.getReviews.and.returnValue(of([]));

    component.ngOnInit();

    expect(component.error).toBe('Livre introuvable dans votre bibliotheque.');
  });

  it('displays error when loading fails', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.getLibrary.and.returnValue(throwError(() => new Error('API Error')));
    bookService.getReviews.and.returnValue(of([]));

    component.ngOnInit();

    expect(component.error).toBe("Impossible de charger l'edition de ce livre.");
    expect(component.loading).toBe(false);
  });

  it('prevents save when component is already saving', () => {
    component.saving = true;
    component.item = mockLibraryItem;

    component.save();

    expect(bookService.updateLibraryItem).not.toHaveBeenCalled();
  });
});
