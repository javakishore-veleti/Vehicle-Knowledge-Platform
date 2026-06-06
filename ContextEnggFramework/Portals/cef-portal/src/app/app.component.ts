import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'cef-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
  <header class="bar">
    <b>🧠 VKP · Context Engineering</b>
    <nav>
      <a routerLink="/chat" routerLinkActive="active">Chat</a>
      <a routerLink="/admin" routerLinkActive="active">Admin</a>
    </nav>
  </header>
  <main><router-outlet></router-outlet></main>
  `,
  styles: [`
    .bar { background:#fff; border-bottom:1px solid var(--line); padding:.7rem 1.2rem; display:flex; align-items:center; gap:1.5rem; }
    .bar nav { display:flex; gap:1rem; } .bar a { text-decoration:none; color:var(--muted); padding:.2rem .1rem; border-bottom:2px solid transparent; }
    .bar a.active { color:var(--accent); border-bottom-color:var(--accent); }
    main { max-width:860px; margin:1rem auto; padding:0 1rem; }
  `]
})
export class AppComponent {}
