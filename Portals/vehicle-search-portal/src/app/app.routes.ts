import { Routes } from '@angular/router';
import { SearchComponent } from './features/search/search.component';
import { LogsListComponent } from './features/logs/logs-list.component';
import { LogDetailComponent } from './features/logs/log-detail.component';

export const routes: Routes = [
  { path: '', component: SearchComponent, title: 'Vehicle Search' },
  { path: 'logs', component: LogsListComponent, title: 'Search Logs' },
  { path: 'logs/:id', component: LogDetailComponent, title: 'Search Log' },
  { path: '**', redirectTo: '' }
];
