import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Book, BookOverview, DashboardOverview, LibraryItem, LibraryUpdate, Review, ReviewPayload } from '../models';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root',
})
export class BookService {
  // Session storage preserves navigation context without leaking it across browser sessions.
  private readonly selectedBookStorageKey = 'selected_book';
  private readonly lastSearchQueryStorageKey = 'last_search_query';

  constructor(private readonly api: ApiService) {}

  searchBooks(query: string): Observable<Book[]> {
    return this.api.get<Book[]>(`/books/search?q=${encodeURIComponent(query)}`);
  }

  getLibrary(): Observable<LibraryItem[]> {
    return this.api.get<LibraryItem[]>(`/library/`);
  }

  addToLibrary(book: Book): Observable<LibraryItem> {
    // Only send the fields owned by the API contract; UI-only flags stay client-side.
    return this.api.post<LibraryItem>(`/library/`, {
      google_book_id: book.google_book_id,
      title: book.title,
      authors: book.authors,
      description: book.description,
      cover_image: book.cover_image,
      published_date: book.published_date,
    });
  }

  removeFromLibrary(bookId: number): Observable<void> {
    return this.api.delete<void>(`/library/${bookId}`);
  }

  updateLibraryItem(bookId: number, payload: LibraryUpdate): Observable<LibraryItem> {
    return this.api.patch<LibraryItem>(`/library/${bookId}`, payload);
  }

  upsertReview(review: ReviewPayload): Observable<Review> {
    return this.api.post<Review>(`/reviews/`, review);
  }

  getReviews(): Observable<Review[]> {
    return this.api.get<Review[]>(`/reviews/`);
  }

  getRecommendations(): Observable<Book[]> {
    return this.api.get<Book[]>(`/recommendations/`);
  }

  getDashboard(): Observable<DashboardOverview> {
    return this.api.get<DashboardOverview>(`/dashboard/`);
  }

  updateReadingGoal(readingGoal: number): Observable<DashboardOverview> {
    return this.api.patch<DashboardOverview>(`/dashboard/goal`, { reading_goal: readingGoal });
  }

  getBookOverview(googleBookId: string): Observable<BookOverview> {
    return this.api.get<BookOverview>(`/books/${googleBookId}/overview`);
  }

  setSelectedBook(book: Book): void {
    // Cache the last opened card so a direct detail refresh can render immediately
    // while the canonical overview request is still loading.
    sessionStorage.setItem(this.selectedBookStorageKey, JSON.stringify(book));
  }

  getSelectedBook(): Book | null {
    const raw = sessionStorage.getItem(this.selectedBookStorageKey);
    return raw ? JSON.parse(raw) as Book : null;
  }

  setLastSearchQuery(query: string): void {
    // Keep the search input stable when the user returns from a detail page.
    sessionStorage.setItem(this.lastSearchQueryStorageKey, query);
  }

  getLastSearchQuery(): string {
    return sessionStorage.getItem(this.lastSearchQueryStorageKey) ?? '';
  }
}
