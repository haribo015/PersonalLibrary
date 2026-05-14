import { of, throwError } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';

import { Book, BookOverview } from '../../models';
import { BookService } from '../../services/book.service';
import { BookDetailsComponent } from './book-details.component';

describe('BookDetailsComponent', () => {
  let route: ActivatedRoute;
  let router: jasmine.SpyObj<Router>;
  let bookService: jasmine.SpyObj<BookService>;
  let component: BookDetailsComponent;

  const book: Book = {
    google_book_id: 'google-1',
    title: 'Clean Code',
  };

  const overview: BookOverview = {
    book,
    google_details: {
      categories: ['Software'],
      language: 'en',
      isbn_13: '9780132350884',
    },
  };

  function createComponent(googleBookId: string | null = 'google-1'): BookDetailsComponent {
    route = {
      snapshot: {
        paramMap: {
          get: jasmine.createSpy('get').and.returnValue(googleBookId),
        },
      },
    } as unknown as ActivatedRoute;
    return new BookDetailsComponent(route, router, bookService);
  }

  beforeEach(() => {
    router = jasmine.createSpyObj<Router>('Router', ['getCurrentNavigation', 'navigate']);
    bookService = jasmine.createSpyObj<BookService>('BookService', [
      'getBookOverview',
      'getLastSearchQuery',
      'getSelectedBook',
    ]);
    router.getCurrentNavigation.and.returnValue({ extras: { state: { book } } } as never);
    bookService.getSelectedBook.and.returnValue(null);
    bookService.getBookOverview.and.returnValue(of(overview));
    component = createComponent();
  });

  it('loads the canonical overview for the route book id', () => {
    component.ngOnInit();

    expect(component.book).toEqual(book);
    expect(component.overview).toEqual(overview);
    expect(component.loading).toBeFalse();
    expect(bookService.getBookOverview).toHaveBeenCalledWith('google-1');
  });

  it('stops loading when there is no route book id', () => {
    component = createComponent(null);

    component.ngOnInit();

    expect(component.loading).toBeFalse();
    expect(bookService.getBookOverview).not.toHaveBeenCalled();
  });

  it('stops loading when overview loading fails', () => {
    bookService.getBookOverview.and.returnValue(throwError(() => new Error('network')));

    component.ngOnInit();

    expect(component.loading).toBeFalse();
  });

  it('formats status, priority, and language labels', () => {
    expect(component.formatStatus('dnf')).toBe('Abandonne');
    expect(component.formatStatus(undefined)).toBe('Non renseigne');
    expect(component.formatPriority('high')).toBe('Haute');
    expect(component.formatPriority(undefined)).toBe('Non renseignee');
    expect(component.formatLanguage('en')).toBe('Anglais');
    expect(component.formatLanguage('pt')).toBe('PT');
    expect(component.formatLanguage(null)).toBe('Non renseignee');
  });

  it('returns to search with the last query when one exists', () => {
    bookService.getLastSearchQuery.and.returnValue('clean code');

    component.returnToSearch();

    expect(router.navigate).toHaveBeenCalledWith(['/search'], { queryParams: { q: 'clean code' } });
  });

  it('returns to search without query params when no query exists', () => {
    bookService.getLastSearchQuery.and.returnValue('');

    component.returnToSearch();

    expect(router.navigate).toHaveBeenCalledWith(['/search']);
  });
});
