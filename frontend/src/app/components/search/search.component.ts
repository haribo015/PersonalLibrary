import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['../../app.component.css'],
})
export class SearchComponent implements OnInit {
  query = '';
  books: Book[] = [];
  loading = false;
  error = '';

  constructor(
    private readonly bookService: BookService,
    public auth: AuthService,
    private readonly router: Router,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    // Restore the previous query for the back-to-search flow from book details.
    const routeQuery = this.route.snapshot.queryParamMap.get('q')?.trim();
    this.query = routeQuery || this.bookService.getLastSearchQuery();
    if (routeQuery) {
      this.search();
    }
  }

  search(): void {
    const trimmedQuery = this.query.trim();
    if (!trimmedQuery) {
      return;
    }

    this.loading = true;
    this.error = '';
    // Persist the normalized query, not accidental leading/trailing spaces.
    this.bookService.setLastSearchQuery(trimmedQuery);
    this.bookService.searchBooks(trimmedQuery).subscribe({
      next: data => {
        this.books = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'La recherche a echoue. Reessayez dans quelques instants.';
        this.loading = false;
      },
    });
  }

  addBook(book: Book): void {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.bookService.addToLibrary(book).subscribe({
      next: () => {
        this.books = this.books.map(item =>
          item.google_book_id === book.google_book_id
            ? { ...item, already_in_library: true }
            : item
        );
      },
      error: () => {
        this.error = "Impossible d'ajouter ce livre a votre bibliotheque.";
      },
    });
  }

  openDetails(book: Book): void {
    const trimmedQuery = this.query.trim();
    if (trimmedQuery) {
      // Save edits made in the search bar even if the user opens a result before submitting.
      this.bookService.setLastSearchQuery(trimmedQuery);
    }
    this.bookService.setSelectedBook(book);
    this.router.navigate(['/books', book.google_book_id], { state: { book } });
  }
}
