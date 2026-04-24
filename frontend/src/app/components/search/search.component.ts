import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['../../app.component.css'],
})
export class SearchComponent {
  query = '';
  books: Book[] = [];
  loading = false;
  error = '';

  constructor(
    private readonly bookService: BookService,
    public auth: AuthService,
    private readonly router: Router,
  ) {}

  search(): void {
    if (!this.query.trim()) {
      return;
    }

    this.loading = true;
    this.error = '';
    this.bookService.searchBooks(this.query).subscribe({
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
    this.bookService.setSelectedBook(book);
    this.router.navigate(['/books', book.google_book_id], { state: { book } });
  }
}
