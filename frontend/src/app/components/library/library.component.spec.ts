import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { LibraryItem } from '../../models';
import { BookService } from '../../services/book.service';
import { LibraryComponent } from './library.component';

describe('LibraryComponent', () => {
  let bookService: jasmine.SpyObj<BookService>;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let component: LibraryComponent;

  beforeEach(() => {
    bookService = jasmine.createSpyObj<BookService>('BookService', ['getLibrary', 'removeFromLibrary']);
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    component = new LibraryComponent(bookService, auth, router);
  });

  it('redirects anonymous users to login', () => {
    auth.isLoggedIn.and.returnValue(false);

    component.ngOnInit();

    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('loads library items when user is authenticated', () => {
    const mockItems: LibraryItem[] = [
      {
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
      },
    ];
    auth.isLoggedIn.and.returnValue(true);
    bookService.getLibrary.and.returnValue(of(mockItems));

    component.ngOnInit();

    expect(bookService.getLibrary).toHaveBeenCalled();
    expect(component.libraryItems).toEqual(mockItems);
    expect(component.loading).toBe(false);
  });

  it('displays error when library fails to load', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.getLibrary.and.returnValue(throwError(() => new Error('API Error')));

    component.ngOnInit();

    expect(component.error).toBe('Impossible de charger votre bibliotheque.');
    expect(component.loading).toBe(false);
  });

  it('reloads library when loadLibrary is called', () => {
    auth.isLoggedIn.and.returnValue(true);
    const mockItems: LibraryItem[] = [];
    bookService.getLibrary.and.returnValue(of(mockItems));

    component.loadLibrary();

    expect(bookService.getLibrary).toHaveBeenCalled();
    expect(component.libraryItems).toEqual(mockItems);
  });
});
