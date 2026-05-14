import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { DashboardOverview } from '../../models';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['../../app.component.css'],
})
export class DashboardComponent implements OnInit {
  dashboard: DashboardOverview | null = null;
  loading = true;
  error = '';
  readingGoal = 24;
  savingGoal = false;

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

    this.bookService.getDashboard().subscribe({
      next: data => {
        this.dashboard = data;
        this.readingGoal = data.reading_goal;
        this.loading = false;
      },
      error: () => {
        this.error = 'Impossible de charger votre dashboard.';
        this.loading = false;
      },
    });
  }

  saveGoal(): void {
    if (this.readingGoal < 1) {
      // Validate locally before hitting the API to avoid an unnecessary round trip.
      this.error = 'L objectif de lecture doit etre superieur a 0.';
      return;
    }

    this.savingGoal = true;
    this.bookService.updateReadingGoal(this.readingGoal).subscribe({
      next: data => {
        this.dashboard = data;
        this.readingGoal = data.reading_goal;
        this.savingGoal = false;
      },
      error: () => {
        this.error = 'Impossible de mettre a jour votre objectif.';
        this.savingGoal = false;
      },
    });
  }

  formatMetricLabel(value: string): string {
    // Backend metrics use stable enum keys; the dashboard translates them for display.
    const labels: Record<string, string> = {
      dnf: 'Abandonne',
      finished: 'Termine',
      high: 'Haute',
      low: 'Basse',
      medium: 'Moyenne',
      paper: 'Papier',
      reading: 'En cours',
      to_read: 'A lire',
    };

    return labels[value] ?? value;
  }
}
