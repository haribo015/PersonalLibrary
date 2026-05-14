import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-recommendations',
  templateUrl: './recommendations.component.html',
  styleUrls: ['../../app.component.css'],
})
export class RecommendationsComponent implements OnInit {
  recommendations: Book[] = [];
  loading = true;
  error = '';

  constructor(
    private readonly bookService: BookService,
    public auth: AuthService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.bookService.getRecommendations().subscribe({
      next: data => {
        this.recommendations = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'Impossible de recuperer les suggestions.';
        this.loading = false;
      },
    });
  }

  addBook(book: Book): void {
    this.bookService.addToLibrary(book).subscribe({
      next: () => {
        // Keep the recommendation card in place but prevent duplicate add attempts.
        this.recommendations = this.recommendations.map(item =>
          item.google_book_id === book.google_book_id
            ? { ...item, already_in_library: true }
            : item
        );
      },
      error: () => {
        this.error = "Impossible d'ajouter cette suggestion a votre bibliotheque.";
      },
    });
  }

  openDetails(book: Book): void {
    // Reuse the detail cache so recommendations feel as responsive as search results.
    this.bookService.setSelectedBook(book);
    this.router.navigate(['/books', book.google_book_id], { state: { book } });
  }
}
