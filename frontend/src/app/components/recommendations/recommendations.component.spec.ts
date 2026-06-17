import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book } from '../../models';
import { BookService } from '../../services/book.service';
import { RecommendationsComponent } from './recommendations.component';

describe('RecommendationsComponent', () => {
  let bookService: jasmine.SpyObj<BookService>;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let component: RecommendationsComponent;

  beforeEach(() => {
    bookService = jasmine.createSpyObj<BookService>('BookService', ['getRecommendations']);
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    component = new RecommendationsComponent(bookService, auth, router);
  });

  it('redirects anonymous users to login', () => {
    auth.isLoggedIn.and.returnValue(false);

    component.ngOnInit();

    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('loads recommendations when user is authenticated', () => {
    const mockBooks: Book[] = [
      { id: 1, google_book_id: 'abc123', title: 'Book 1', authors: 'Author 1', description: '', cover_image: '', published_date: '' },
    ];
    auth.isLoggedIn.and.returnValue(true);
    bookService.getRecommendations.and.returnValue(of(mockBooks));

    component.ngOnInit();

    expect(bookService.getRecommendations).toHaveBeenCalled();
    expect(component.recommendations).toEqual(mockBooks);
    expect(component.loading).toBe(false);
  });

  it('displays error when recommendations fail to load', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.getRecommendations.and.returnValue(throwError(() => new Error('API Error')));

    component.ngOnInit();

    expect(component.error).toBe('Impossible de recuperer les suggestions.');
    expect(component.loading).toBe(false);
  });
});
