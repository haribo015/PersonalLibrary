import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { DashboardOverview } from '../../models';
import { BookService } from '../../services/book.service';
import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  let bookService: jasmine.SpyObj<BookService>;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let component: DashboardComponent;

  beforeEach(() => {
    bookService = jasmine.createSpyObj<BookService>('BookService', ['getDashboard', 'updateReadingGoal']);
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    component = new DashboardComponent(bookService, auth, router);
  });

  it('redirects anonymous users to login', () => {
    auth.isLoggedIn.and.returnValue(false);

    component.ngOnInit();

    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('loads dashboard data when user is authenticated', () => {
    const mockDashboard: DashboardOverview = {
      books_in_library: 5,
      books_read_this_year: 2,
      books_in_progress: 1,
      books_to_read: 2,
      books_dnf: 0,
      favorite_books: 3,
      completion_rate: 0.4,
      average_rating: 4.5,
      reading_goal: 24,
      reading_goal_progress: 2,
      categories: [],
      formats: [],
      statuses: [],
      priorities: [],
      top_tags: [],
    };
    auth.isLoggedIn.and.returnValue(true);
    bookService.getDashboard.and.returnValue(of(mockDashboard));

    component.ngOnInit();

    expect(bookService.getDashboard).toHaveBeenCalled();
    expect(component.dashboard).toEqual(mockDashboard);
    expect(component.readingGoal).toBe(24);
    expect(component.loading).toBe(false);
  });

  it('displays error when dashboard fails to load', () => {
    auth.isLoggedIn.and.returnValue(true);
    bookService.getDashboard.and.returnValue(throwError(() => new Error('API Error')));

    component.ngOnInit();

    expect(component.error).toBe('Impossible de charger votre dashboard.');
    expect(component.loading).toBe(false);
  });

    it('validates reading goal before saving', () => {
        component.readingGoal = 0;

        component.saveGoal();

        expect(component.error).toBe('L objectif de lecture doit etre superieur a 0.');
        
        expect(bookService.updateReadingGoal).not.toHaveBeenCalled();
        expect(bookService.getDashboard).not.toHaveBeenCalled();
    });
});
