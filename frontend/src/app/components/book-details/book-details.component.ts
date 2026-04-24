import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Book, BookOverview } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-book-details',
  templateUrl: './book-details.component.html',
  styleUrls: ['../../app.component.css'],
})
export class BookDetailsComponent implements OnInit {
  book: Book | null = null;
  overview: BookOverview | null = null;
  loading = true;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly bookService: BookService,
  ) {}

  ngOnInit(): void {
    const navigationBook = this.router.getCurrentNavigation()?.extras.state?.['book'] as Book | undefined;
    const historyBook = history.state?.book as Book | undefined;
    const cachedBook = this.bookService.getSelectedBook();
    const googleBookId = this.route.snapshot.paramMap.get('googleBookId');

    this.book = navigationBook
      ?? historyBook
      ?? (cachedBook && cachedBook.google_book_id === googleBookId ? cachedBook : null);

    if (!googleBookId) {
      this.loading = false;
      return;
    }

    this.bookService.getBookOverview(googleBookId).subscribe({
      next: overview => {
        this.overview = overview;
        this.book = overview.book;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  formatStatus(status: string | undefined): string {
    const labels: Record<string, string> = {
      to_read: 'A lire',
      reading: 'En cours',
      finished: 'Termine',
      paused: 'En pause',
      dnf: 'DNF',
    };
    return status ? (labels[status] ?? status) : 'Non renseigne';
  }

  formatPriority(priority: string | undefined): string {
    const labels: Record<string, string> = {
      low: 'Basse',
      medium: 'Moyenne',
      high: 'Haute',
    };
    return priority ? (labels[priority] ?? priority) : 'Non renseignee';
  }

  formatLanguage(language: string | undefined | null): string {
    const labels: Record<string, string> = {
      fr: 'Francais',
      en: 'Anglais',
      es: 'Espagnol',
      de: 'Allemand',
      it: 'Italien',
    };
    return language ? (labels[language] ?? language.toUpperCase()) : 'Non renseignee';
  }
}
