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
    private bookService: BookService,
    public auth: AuthService,
    private router: Router,
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
}
