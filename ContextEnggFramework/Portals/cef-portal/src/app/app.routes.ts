import { Routes } from '@angular/router';
import { ChatComponent } from './features/chat.component';
import { AdminComponent } from './features/admin.component';
import { LogsListComponent } from './features/logs-list.component';
import { LogDetailComponent } from './features/log-detail.component';

export const routes: Routes = [
  { path: '', redirectTo: 'chat', pathMatch: 'full' },
  { path: 'chat', component: ChatComponent, title: 'Context-Aware Chat' },
  { path: 'admin', component: AdminComponent, title: 'CEF Admin' },
  { path: 'logs', component: LogsListComponent, title: 'Chat Logs' },
  { path: 'logs/:id', component: LogDetailComponent, title: 'Chat Log' },
  { path: '**', redirectTo: 'chat' }
];
