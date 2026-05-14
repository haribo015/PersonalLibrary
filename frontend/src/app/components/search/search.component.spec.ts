import { of, throwError } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book } from '../../models';
import { BookService } from '../../services/book.service';
import { SearchComponent } from './search.component';

describe('SearchComponent', () => {
  let bookService: jasmine.SpyObj<BookService>;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let route: ActivatedRoute;
  let component: SearchComponent;

  const book: Book = {
    google_book_id: 'google-1',
    title: 'Clean Code',
  };

  function createComponent(routeQuery: string | null = null): SearchComponent {
    route = {
      snapshot: {
        queryParamMap: {
          get: jasmine.createSpy('get').and.returnValue(routeQuery),
        },
      },
    } as unknown as ActivatedRoute;
    return new SearchComponent(bookService, auth, router, route);
  }

  beforeEach(() => {
    bookService = jasmine.createSpyObj<BookService>('BookService', [
      'addToLibrary',
      'getLastSearchQuery',
      'searchBooks',
      'setLastSearchQuery',
      'setSelectedBook',
    ]);
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    bookService.getLastSearchQuery.and.returnValue('cached query');
    bookService.searchBooks.and.returnValue(of([book]));
    component = createComponent();
  });

  it('restores the query from session storage when no route query is provided', () => {
    component.ngOnInit();

    expect(component.query).toBe('cached query');
    expect(bookService.searchBooks).not.toHaveBeenCalled();
  });

  it('uses the route query and launches a search when returning from details', () => {
    component = createComponent(' clean code ');

    component.ngOnInit();

    expect(component.query).toBe('clean code');
    expect(bookService.setLastSearchQuery).toHaveBeenCalledWith('clean code');
    expect(bookService.searchBooks).toHaveBeenCalledWith('clean code');
    expect(component.books).toEqual([book]);
    expect(component.loading).toBeFalse();
  });

  it('does not search blank queries', () => {
    component.query = '   ';

    component.search();

    expect(bookService.searchBooks).not.toHaveBeenCalled();
  });

  it('stores the selected query and navigates to details', () => {
    component.query = ' clean code ';

    component.openDetails(book);

    expect(bookService.setLastSearchQuery).toHaveBeenCalledWith('clean code');
    expect(bookService.setSelectedBook).toHaveBeenCalledWith(book);
    expect(router.navigate).toHaveBeenCalledWith(['/books', 'google-1'], { state: { book } });
  });

  it('redirects anonymous users to login before adding a book', () => {
    auth.isLoggedIn.and.returnValue(false);

    component.addBook(book);

    expect(router.navigate).toHaveBeenCalledWith(['/login']);
    expect(bookService.addToLibrary).not.toHaveBeenCalled();
  });

  it('marks an added book as already saved', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.addToLibrary.and.returnValue(of({} as never));
    component.books = [book];

    component.addBook(book);

    expect(component.books[0].already_in_library).toBeTrue();
  });

  it('shows an error when the search request fails', () => {
    bookService.searchBooks.and.returnValue(throwError(() => new Error('network')));
    component.query = 'clean code';

    component.search();

    expect(component.error).toBe('La recherche a echoue. Reessayez dans quelques instants.');
    expect(component.loading).toBeFalse();
  });
});
