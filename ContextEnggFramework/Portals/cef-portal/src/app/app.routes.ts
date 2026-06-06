import { Routes } from '@angular/router';
import { ChatComponent } from './features/chat.component';
import { AdminComponent } from './features/admin.component';

export const routes: Routes = [
  { path: '', redirectTo: 'chat', pathMatch: 'full' },
  { path: 'chat', component: ChatComponent, title: 'Context-Aware Chat' },
  { path: 'admin', component: AdminComponent, title: 'CEF Admin' },
  { path: '**', redirectTo: 'chat' }
];
