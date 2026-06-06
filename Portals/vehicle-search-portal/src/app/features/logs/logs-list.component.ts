import { Component, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ExploreService, LogListItem } from '../../core/explore.service';

/** Search Logs — lists veh_search_request_log rows. Two paging modes:
 *  server (20/page via ?page&size) or client (fetch latest 1000, page locally). */
@Component({
  selector: 'vs-logs',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="logs-head">
    <h1>Search Logs</h1>
    <p class="vs-sub">Every search recorded with its full flow, tech stack, indexes, LLMs and vendors.</p>
  </div>

  <div class="bar">
    <div class="seg">
      <button [class.on]="mode()==='server'" (click)="setMode('server')">Server-side (20/page)</button>
      <button [class.on]="mode()==='client'" (click)="setMode('client')">Client-side (latest 1000)</button>
    </div>
    <span class="sp"></span>
    <label>Store
      <select [(ngModel)]="store" (change)="reload()">
        <option value="">any</option><option value="pgvector">pgVector</option><option value="mongodb">MongoDB</option>
      </select>
    </label>
    <label>Status
      <select [(ngModel)]="status" (change)="reload()">
        <option value="">any</option><option value="llm">llm</option><option value="extractive">extractive</option>
        <option value="blocked">blocked</option><option value="none">none</option>
      </select>
    </label>
    <button class="refresh" (click)="reload()">↻ Refresh</button>
  </div>

  <div *ngIf="error()" class="vs-error">{{ error() }}</div>
  <div *ngIf="loading()" class="vs-skeleton">Loading logs…</div>

  <div class="rows" *ngIf="!loading() && pageItems().length">
    <a class="row" *ngFor="let r of pageItems()" [routerLink]="['/logs', r.id]">
      <div class="r-main">
        <div class="r-title">{{ r.title }}</div>
        <div class="r-sub">
          <span class="tag store">{{ r.store }}</span>
          <span class="tag">{{ r.mode }}</span>
          <span class="tag fw">{{ r.framework }}</span>
          <span class="tag origin">⚲ {{ r.origin_source }}</span>
          <span class="tag" *ngIf="r.llm_enabled">LLM</span>
          <span class="tag" *ngFor="let v of (r.vendors || []).slice(0,3)">{{ v.name }}</span>
        </div>
      </div>
      <div class="r-meta">
        <span class="badge" [attr.data-st]="r.status">{{ r.status }}</span>
        <span class="m">{{ r.result_count }} src</span>
        <span class="m">{{ r.latency_ms }} ms</span>
        <span class="m dt">{{ r.created_dt | date:'MMM d, HH:mm:ss' }}</span>
        <span class="chev">›</span>
      </div>
    </a>
  </div>

  <div *ngIf="!loading() && !pageItems().length && !error()" class="vs-empty">
    No search logs yet — run a search, then come back.
  </div>

  <div class="pager" *ngIf="!loading() && total() > size">
    <button (click)="prev()" [disabled]="page()===0">‹ Prev</button>
    <span>Page {{ page()+1 }} / {{ totalPages() }} · {{ total() }} rows ({{ mode() }})</span>
    <button (click)="next()" [disabled]="page()+1>=totalPages()">Next ›</button>
  </div>
  `,
  styles: [`
    .logs-head h1 { margin:.2rem 0 .1rem; background:var(--vs-grad); -webkit-background-clip:text; background-clip:text; color:transparent; font-size:1.6rem; }
    .bar { display:flex; flex-wrap:wrap; align-items:center; gap:.6rem; margin:.8rem 0 1rem; }
    .bar .sp { flex:1; }
    .bar label { font-size:.8rem; color:var(--vs-muted); font-weight:600; display:flex; align-items:center; gap:.35rem; }
    .bar select { padding:.3rem .5rem; border:1px solid var(--vs-border); border-radius:8px; background:#fff; font-weight:600; color:var(--vs-text); }
    .seg { display:inline-flex; background:#f1ecfe; border-radius:999px; padding:3px; }
    .seg button { border:0; background:transparent; padding:.4rem .9rem; border-radius:999px; cursor:pointer; font-weight:700; font-size:.82rem; color:#7c3aed; }
    .seg button.on { background:var(--vs-grad); color:#fff; box-shadow:0 4px 12px rgba(124,58,237,.3); }
    .refresh { border:1px solid var(--vs-border); background:#fff; border-radius:8px; padding:.35rem .7rem; cursor:pointer; color:var(--vs-brand); font-weight:600; }
    .rows { display:flex; flex-direction:column; gap:.55rem; }
    .row { display:flex; align-items:center; justify-content:space-between; gap:1rem; text-decoration:none; color:inherit;
      background:#fff; border:1px solid var(--vs-border); border-radius:12px; padding:.7rem .9rem; box-shadow:0 1px 2px rgba(124,58,237,.07); transition:transform .12s, box-shadow .12s, border-color .12s; }
    .row:hover { transform:translateY(-1px); box-shadow:0 10px 24px rgba(124,58,237,.14); border-color:#d6c7fb; }
    .r-title { font-weight:700; color:var(--vs-text); margin-bottom:.3rem; }
    .r-sub { display:flex; flex-wrap:wrap; gap:.3rem; }
    .tag { font-size:.68rem; font-weight:700; color:#7c3aed; background:#f1ecfe; border:1px solid #e4d4ff; border-radius:999px; padding:.08rem .5rem; }
    .tag.store { color:#0f8a5f; background:#e7faf1; border-color:#c5f0db; }
    .tag.fw { color:#be185d; background:#fdeef6; border-color:#f9d7e8; }
    .tag.origin { color:#b45309; background:#fff5e6; border-color:#fde0b0; }
    .r-meta { display:flex; align-items:center; gap:.7rem; white-space:nowrap; }
    .r-meta .m { font-size:.74rem; color:var(--vs-muted); }
    .r-meta .dt { color:var(--vs-faint, #94a3b8); }
    .badge { font-size:.66rem; font-weight:800; text-transform:uppercase; padding:.12rem .5rem; border-radius:999px; background:#f1ecfe; color:#7c3aed; }
    .badge[data-st=blocked], .badge[data-st=none] { background:#fde8e8; color:#c0392b; }
    .badge[data-st=llm] { background:#e7faf1; color:#0f8a5f; }
    .chev { color:#c4b5fd; font-size:1.3rem; font-weight:700; }
    .pager { display:flex; align-items:center; justify-content:center; gap:1rem; margin:1.2rem 0; color:var(--vs-muted); font-size:.85rem; }
    .pager button { border:1px solid var(--vs-border); background:#fff; border-radius:8px; padding:.4rem .9rem; cursor:pointer; color:var(--vs-brand); font-weight:700; }
    .pager button:disabled { opacity:.45; cursor:default; }
  `]
})
export class LogsListComponent implements OnInit {
  readonly mode = signal<'server' | 'client'>('server');
  readonly loading = signal(false);
  readonly error = signal('');
  readonly page = signal(0);
  readonly size = 20;
  store = '';
  status = '';

  private readonly serverItems = signal<LogListItem[]>([]);
  private readonly serverTotal = signal(0);
  private readonly clientItems = signal<LogListItem[]>([]);   // latest 1000 for client-side paging

  readonly total = computed(() => this.mode() === 'server' ? this.serverTotal() : this.clientItems().length);
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / this.size)));
  readonly pageItems = computed(() =>
    this.mode() === 'server'
      ? this.serverItems()
      : this.clientItems().slice(this.page() * this.size, this.page() * this.size + this.size));

  constructor(private explore: ExploreService) {}

  ngOnInit(): void { this.reload(); }

  setMode(m: 'server' | 'client'): void { if (m !== this.mode()) { this.mode.set(m); this.page.set(0); this.reload(); } }

  reload(): void {
    this.loading.set(true); this.error.set('');
    const filt = { store: this.store || undefined, status: this.status || undefined };
    if (this.mode() === 'client') {
      this.explore.logs({ limit: 1000, ...filt }).subscribe({
        next: r => { this.clientItems.set(r.items); this.loading.set(false); },
        error: () => { this.error.set('Could not load logs (is vehicle-explore-service :8090 up?).'); this.loading.set(false); }
      });
    } else {
      this.explore.logs({ page: this.page(), size: this.size, ...filt }).subscribe({
        next: r => { this.serverItems.set(r.items); this.serverTotal.set(r.total ?? r.count); this.loading.set(false); },
        error: () => { this.error.set('Could not load logs (is vehicle-explore-service :8090 up?).'); this.loading.set(false); }
      });
    }
  }

  prev(): void { if (this.page() > 0) { this.page.update(p => p - 1); if (this.mode() === 'server') { this.reload(); } } }
  next(): void { if (this.page() + 1 < this.totalPages()) { this.page.update(p => p + 1); if (this.mode() === 'server') { this.reload(); } } }
}
