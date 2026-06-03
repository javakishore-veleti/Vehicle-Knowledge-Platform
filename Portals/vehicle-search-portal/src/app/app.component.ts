import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
  <header class="vs-topbar">
    <div class="vs-brand"><i class="pi pi-car"></i> VKP <span>Vehicle Search</span></div>
    <div class="vs-topbar-right"><i class="pi pi-search"></i> Powered by semantic search</div>
  </header>
  <main class="vs-main">
    <router-outlet></router-outlet>
  </main>
  `
})
export class AppComponent {}
