import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
  <header class="vs-topbar">
    <a routerLink="/" class="vs-brand"><i class="pi pi-car"></i> VKP <span>Vehicle Search</span></a>
    <nav class="vs-nav">
      <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Search</a>
      <a routerLink="/logs" routerLinkActive="active">Logs</a>
    </nav>
    <div class="vs-topbar-right"><i class="pi pi-search"></i> Powered by semantic search</div>
  </header>
  <main class="vs-main">
    <router-outlet></router-outlet>
  </main>
  `,
  styles: [`
    .vs-brand { text-decoration:none; }
    .vs-nav { display:flex; gap:.3rem; margin-left:1.5rem; }
    .vs-nav a { text-decoration:none; color:var(--vs-muted); font-weight:600; font-size:.9rem; padding:.4rem .85rem; border-radius:9px; }
    .vs-nav a:hover { color:var(--vs-brand); background:#f1ecfe; }
    .vs-nav a.active { color:var(--vs-brand); background:#f1ecfe; }
  `]
})
export class AppComponent {}
