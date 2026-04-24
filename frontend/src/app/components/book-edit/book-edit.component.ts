import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';

import { AuthService } from '../../auth.service';
import { LibraryItem, LibraryUpdate, ReviewPayload } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-book-edit',
  templateUrl: './book-edit.component.html',
  styleUrls: ['../../app.component.css'],
})
export class BookEditComponent implements OnInit {
  item: LibraryItem | null = null;
  loading = true;
  saving = false;
  error = '';
  reviewComment = '';
  rating = 5;
  readonly categories = ['General', 'Roman', 'Essai', 'Science-fiction', 'Fantasy', 'Business', 'Biographie'];
  readonly statuses = ['to_read', 'reading', 'finished', 'paused', 'dnf'];
  readonly priorities = ['low', 'medium', 'high'];
  readonly formats = ['paper', 'ebook', 'audiobook'];

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly bookService: BookService,
    public auth: AuthService,
  ) {}

  ngOnInit(): void {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    const navigationItem = this.router.getCurrentNavigation()?.extras.state?.['item'] as LibraryItem | undefined;
    const bookId = Number(this.route.snapshot.paramMap.get('bookId'));

    if (navigationItem?.book_id === bookId) {
      this.item = this.cloneItem(navigationItem);
    }

    forkJoin({
      items: this.bookService.getLibrary(),
      reviews: this.bookService.getReviews(),
    }).subscribe({
      next: ({ items, reviews }) => {
        const current = items.find(entry => entry.book_id === bookId);
        if (!current && !this.item) {
          this.error = 'Livre introuvable dans votre bibliotheque.';
          this.loading = false;
          return;
        }

        this.item = this.cloneItem(current ?? this.item);
        const review = reviews.find(entry => entry.book_id === this.item.book_id);
        this.rating = review?.rating ?? 5;
        this.reviewComment = review?.comment ?? '';
        this.loading = false;
      },
      error: () => {
        this.error = "Impossible de charger l'edition de ce livre.";
        this.loading = false;
      },
    });
  }

  save(): void {
    if (!this.item || this.saving) {
      return;
    }

    this.error = '';
    this.saving = true;

    const payload: LibraryUpdate = {
      category: this.item.category,
      reading_status: this.item.reading_status,
      priority: this.item.priority,
      reading_format: this.item.reading_format,
      pages_total: this.item.pages_total ?? null,
      pages_read: this.item.pages_read ?? null,
      started_at: this.item.started_at ?? null,
      finished_at: this.item.finished_at ?? null,
      personal_notes: this.item.personal_notes ?? null,
      favorite: this.item.favorite,
      tags: this.item.tags ?? null,
    };

    const reviewPayload: ReviewPayload = {
      book_id: this.item.book_id,
      rating: this.rating,
      comment: this.reviewComment.trim() || '',
    };

    forkJoin({
      item: this.bookService.updateLibraryItem(this.item.book_id, payload),
      review: this.bookService.upsertReview(reviewPayload),
    }).subscribe({
      next: ({ item }) => {
        this.bookService.setSelectedBook(item.book);
        this.router.navigate(['/books', item.book.google_book_id], { state: { book: item.book } });
      },
      error: (response) => {
        this.error = response?.error?.detail ?? "Impossible d'enregistrer les modifications.";
        this.saving = false;
      },
    });
  }

  formatStatus(status: string): string {
    const labels: Record<string, string> = {
      to_read: 'A lire',
      reading: 'En cours',
      finished: 'Termine',
      paused: 'En pause',
      dnf: 'DNF',
    };
    return labels[status] ?? status;
  }

  formatPriority(priority: string): string {
    const labels: Record<string, string> = {
      low: 'Basse',
      medium: 'Moyenne',
      high: 'Haute',
    };
    return labels[priority] ?? priority;
  }

  private cloneItem(item: LibraryItem | null): LibraryItem {
    if (!item) {
      throw new Error('Aucun livre disponible pour la duplication.');
    }
    return {
      ...item,
      book: { ...item.book },
    };
  }
}
