import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'cef-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
  <header class="bar">
    <div class="brand">
      <span class="orb">🧠</span>
      <div class="brand-txt">
        <b>VKP Context Engineering</b>
        <small>Context-aware vehicle intelligence</small>
      </div>
    </div>
    <nav>
      <a routerLink="/chat" routerLinkActive="active">Chat</a>
      <a routerLink="/logs" routerLinkActive="active">Logs</a>
      <a routerLink="/admin" routerLinkActive="active">Admin</a>
    </nav>
  </header>
  <main><router-outlet></router-outlet></main>
  `,
  styles: [`
    :host { display:flex; flex-direction:column; min-height:100vh; }
    .bar {
      position:sticky; top:0; z-index:10;
      background:rgba(255,255,255,.82); backdrop-filter:saturate(1.4) blur(10px);
      border-bottom:1px solid var(--line); box-shadow:var(--shadow-sm);
      padding:.7rem 1.4rem; display:flex; align-items:center; justify-content:space-between; gap:1.5rem;
    }
    .brand { display:flex; align-items:center; gap:.7rem; }
    .orb {
      width:38px; height:38px; border-radius:11px; background:var(--grad); color:#fff;
      display:grid; place-items:center; font-size:1.15rem;
      box-shadow:0 6px 16px rgba(79,70,229,.35);
    }
    .brand-txt { display:flex; flex-direction:column; line-height:1.15; }
    .brand-txt b { font-size:.98rem; letter-spacing:.1px; }
    .brand-txt small { color:var(--muted); font-size:.72rem; }
    nav { display:flex; gap:.35rem; }
    nav a {
      text-decoration:none; color:var(--muted); font-weight:600; font-size:.9rem;
      padding:.45rem .9rem; border-radius:9px; transition:all .15s;
    }
    nav a:hover { color:var(--ink); background:#f1f3f9; }
    nav a.active { color:var(--accent); background:var(--accent-soft); }
    main { flex:1; width:100%; max-width:1000px; margin:0 auto; padding:1.25rem 1rem 1.5rem; display:flex; flex-direction:column; }
  `]
})
export class AppComponent {}
