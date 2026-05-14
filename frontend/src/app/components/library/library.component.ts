import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { Book, LibraryItem, LibraryUpdate } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['../../app.component.css'],
})
export class LibraryComponent implements OnInit {
  libraryItems: LibraryItem[] = [];
  loading = true;
  error = '';
  selectedStatus = 'all';
  selectedCategory = 'all';
  selectedPriority = 'all';
  sortBy = 'recent';
  readonly categories = ['General', 'Roman', 'Essai', 'Science-fiction', 'Fantasy', 'Business', 'Biographie'];
  readonly statuses = ['to_read', 'reading', 'finished', 'paused', 'dnf'];
  readonly priorities = ['low', 'medium', 'high'];
  readonly formats = ['paper', 'ebook', 'audiobook'];

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

    this.loadLibrary();
  }

  loadLibrary(): void {
    this.loading = true;
    this.error = '';
    this.bookService.getLibrary().subscribe({
      next: items => {
        this.libraryItems = items;
        this.loading = false;
      },
      error: () => {
        this.error = 'Impossible de charger votre bibliotheque.';
        this.loading = false;
      },
    });
  }

  removeBook(bookId: number): void {
    this.bookService.removeFromLibrary(bookId).subscribe({
      next: () => {
        this.libraryItems = this.libraryItems.filter(item => item.book_id !== bookId);
      },
      error: () => {
        this.error = 'Impossible de retirer ce livre.';
      },
    });
  }

  openDetails(book: Book): void {
    this.bookService.setSelectedBook(book);
    this.router.navigate(['/books', book.google_book_id], { state: { book } });
  }

  openEdit(item: LibraryItem): void {
    this.bookService.setSelectedBook(item.book);
    this.router.navigate(['/library', item.book_id, 'edit'], { state: { item } });
  }

  get filteredLibraryItems(): LibraryItem[] {
    // Derive the visible list from immutable copies so filtering and sorting never
    // reorder the source array returned by the backend.
    return [...this.libraryItems]
      .filter(item => this.selectedStatus === 'all' || item.reading_status === this.selectedStatus)
      .filter(item => this.selectedCategory === 'all' || item.category === this.selectedCategory)
      .filter(item => this.selectedPriority === 'all' || item.priority === this.selectedPriority)
      .sort((left, right) => this.compareItems(left, right));
  }

  get availableCategories(): string[] {
    const dynamicCategories = this.libraryItems
      .map(item => item.category)
      .filter((category): category is string => Boolean(category));
    return Array.from(new Set([...this.categories, ...dynamicCategories]));
  }

  formatStatus(status: string): string {
    const labels: Record<string, string> = {
      to_read: 'A lire',
      reading: 'En cours',
      finished: 'Termine',
      paused: 'En pause',
      dnf: 'Abandonne',
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

  updateMetadata(item: LibraryItem): void {
    const payload: LibraryUpdate = {
      // Persist quick inline changes using the same DTO as the edit screen.
      category: item.category,
      reading_status: item.reading_status,
      priority: item.priority,
      reading_format: item.reading_format,
      pages_total: item.pages_total ?? null,
      pages_read: item.pages_read ?? null,
      started_at: item.started_at ?? null,
      finished_at: item.finished_at ?? null,
      personal_notes: item.personal_notes ?? null,
      favorite: item.favorite,
      tags: item.tags ?? null,
    };

    this.bookService.updateLibraryItem(item.book_id, payload).subscribe({
      next: updated => {
        this.libraryItems = this.libraryItems.map(current =>
          current.book_id === updated.book_id ? updated : current
        );
      },
      error: () => {
        this.error = "Impossible de mettre a jour les informations de lecture.";
      },
    });
  }

  toggleFavorite(item: LibraryItem): void {
    // Optimistic local toggle keeps the UI responsive; updateMetadata persists it.
    item.favorite = !item.favorite;
    this.updateMetadata(item);
  }
  private compareItems(left: LibraryItem, right: LibraryItem): number {
    switch (this.sortBy) {
      case 'title':
        return left.book.title.localeCompare(right.book.title);
      case 'status':
        return left.reading_status.localeCompare(right.reading_status);
      case 'progress':
        return (right.pages_read ?? 0) - (left.pages_read ?? 0);
      case 'priority':
        return this.priorityWeight(right.priority) - this.priorityWeight(left.priority);
      case 'recent':
      default:
        return new Date(right.created_at).getTime() - new Date(left.created_at).getTime();
    }
  }

  private priorityWeight(priority: string): number {
    const weights: Record<string, number> = {
      low: 1,
      medium: 2,
      high: 3,
    };
    return weights[priority] ?? 0;
  }
}
