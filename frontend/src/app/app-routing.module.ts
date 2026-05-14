import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { BookEditComponent } from './components/book-edit/book-edit.component';
import { BookDetailsComponent } from './components/book-details/book-details.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LibraryComponent } from './components/library/library.component';
import { LoginComponent } from './components/login/login.component';
import { RecommendationsComponent } from './components/recommendations/recommendations.component';
import { RegisterComponent } from './components/register/register.component';
import { SearchComponent } from './components/search/search.component';
import { authGuard } from './auth.guard';

const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  // Product routes are guarded here so components can stay focused on their data flows.
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'books/:googleBookId', component: BookDetailsComponent, canActivate: [authGuard] },
  { path: 'library/:bookId/edit', component: BookEditComponent, canActivate: [authGuard] },
  { path: 'search', component: SearchComponent, canActivate: [authGuard] },
  { path: 'library', component: LibraryComponent, canActivate: [authGuard] },
  { path: 'recommendations', component: RecommendationsComponent, canActivate: [authGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
