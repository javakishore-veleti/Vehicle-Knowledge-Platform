import { Component, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CefService, CefLogItem } from '../core/cef.service';

/** Chat Logs — lists cef_chat_request_log rows. Server-side (20/page) or client-side (latest 1000). */
@Component({
  selector: 'cef-logs',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="head"><h2>Chat Logs</h2><p>Every orchestrate call recorded with its full CEF pipeline, scope, strategies, indexes, reasoning engine and vendors.</p></div>

  <div class="bar">
    <div class="seg">
      <button [class.on]="mode()==='server'" (click)="setMode('server')">Server-side (20/page)</button>
      <button [class.on]="mode()==='client'" (click)="setMode('client')">Client-side (latest 1000)</button>
    </div>
    <span class="sp"></span>
    <label>Status
      <select [(ngModel)]="status" (change)="reload()">
        <option value="">any</option><option value="ok">ok</option>
      </select>
    </label>
    <button class="refresh" (click)="reload()">↻ Refresh</button>
  </div>

  <div *ngIf="error()" class="err">{{ error() }}</div>
  <div *ngIf="loading()" class="muted">Loading logs…</div>

  <div class="rows" *ngIf="!loading() && pageItems().length">
    <a class="row" *ngFor="let r of pageItems()" [routerLink]="['/logs', r.id]">
      <div class="r-main">
        <div class="r-title">{{ r.title }}</div>
        <div class="r-sub">
          <span class="tag kb">{{ r.knowledge_base }}</span>
          <span class="tag">{{ r.role }}</span>
          <span class="tag model">{{ r.model }}</span>
          <span class="tag origin">⚲ {{ r.origin_source }}</span>
          <span class="tag" *ngFor="let v of (r.vendors || []).slice(0,3)">{{ v.name }}</span>
        </div>
      </div>
      <div class="r-meta">
        <span class="badge" [attr.data-st]="r.status">{{ r.status }}</span>
        <span class="m">ret {{ r.retrieved }}/used {{ r.used }}</span>
        <span class="m">mem {{ r.memory_turns }}</span>
        <span class="m">{{ r.latency_ms }} ms</span>
        <span class="m dt">{{ r.created_dt | date:'MMM d, HH:mm:ss' }}</span>
        <span class="chev">›</span>
      </div>
    </a>
  </div>

  <div *ngIf="!loading() && !pageItems().length && !error()" class="muted">No chat logs yet — send a chat message, then come back.</div>

  <div class="pager" *ngIf="!loading() && total() > size">
    <button (click)="prev()" [disabled]="page()===0">‹ Prev</button>
    <span>Page {{ page()+1 }} / {{ totalPages() }} · {{ total() }} rows ({{ mode() }})</span>
    <button (click)="next()" [disabled]="page()+1>=totalPages()">Next ›</button>
  </div>
  `,
  styles: [`
    .head h2 { margin:.2rem 0 .1rem; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; font-size:1.5rem; }
    .head p { margin:0 0 .6rem; color:var(--muted); font-size:.84rem; }
    .bar { display:flex; flex-wrap:wrap; align-items:center; gap:.6rem; margin:.4rem 0 1rem; }
    .bar .sp { flex:1; } .bar label { font-size:.8rem; color:var(--muted); font-weight:600; display:flex; align-items:center; gap:.35rem; }
    .bar select { padding:.3rem .5rem; border:1px solid var(--line); border-radius:8px; background:#fff; font-weight:600; color:var(--ink); }
    .seg { display:inline-flex; background:#f1ecfe; border-radius:999px; padding:3px; }
    .seg button { border:0; background:transparent; padding:.4rem .9rem; border-radius:999px; cursor:pointer; font-weight:700; font-size:.82rem; color:#7c3aed; }
    .seg button.on { background:var(--grad); color:#fff; }
    .refresh { border:1px solid var(--line); background:#fff; border-radius:8px; padding:.35rem .7rem; cursor:pointer; color:var(--accent); font-weight:600; }
    .err { background:#fff1f4; color:#be123c; border:1px solid #fbcfe0; padding:.5rem .7rem; border-radius:8px; }
    .muted { color:var(--muted); text-align:center; padding:1.5rem; }
    .rows { display:flex; flex-direction:column; gap:.55rem; }
    .row { display:flex; align-items:center; justify-content:space-between; gap:1rem; text-decoration:none; color:inherit;
      background:#fff; border:1px solid var(--line); border-radius:12px; padding:.7rem .9rem; box-shadow:var(--shadow-sm); transition:transform .12s, box-shadow .12s; }
    .row:hover { transform:translateY(-1px); box-shadow:var(--shadow); }
    .r-title { font-weight:700; color:var(--ink); margin-bottom:.3rem; }
    .r-sub { display:flex; flex-wrap:wrap; gap:.3rem; }
    .tag { font-size:.68rem; font-weight:700; color:#7c3aed; background:#f1ecfe; border:1px solid #e4d4ff; border-radius:999px; padding:.08rem .5rem; }
    .tag.kb { color:#0f8a5f; background:#e7faf1; border-color:#c5f0db; }
    .tag.model { color:#be185d; background:#fdeef6; border-color:#f9d7e8; }
    .tag.origin { color:#b45309; background:#fff5e6; border-color:#fde0b0; }
    .r-meta { display:flex; align-items:center; gap:.7rem; white-space:nowrap; }
    .r-meta .m { font-size:.74rem; color:var(--muted); }
    .badge { font-size:.66rem; font-weight:800; text-transform:uppercase; padding:.12rem .5rem; border-radius:999px; background:#e7faf1; color:#0f8a5f; }
    .chev { color:#c4b5fd; font-size:1.3rem; font-weight:700; }
    .pager { display:flex; align-items:center; justify-content:center; gap:1rem; margin:1.2rem 0; color:var(--muted); font-size:.85rem; }
    .pager button { border:1px solid var(--line); background:#fff; border-radius:8px; padding:.4rem .9rem; cursor:pointer; color:var(--accent); font-weight:700; }
    .pager button:disabled { opacity:.45; cursor:default; }
  `]
})
export class LogsListComponent implements OnInit {
  readonly mode = signal<'server' | 'client'>('server');
  readonly loading = signal(false);
  readonly error = signal('');
  readonly page = signal(0);
  readonly size = 20;
  status = '';

  private readonly serverItems = signal<CefLogItem[]>([]);
  private readonly serverTotal = signal(0);
  private readonly clientItems = signal<CefLogItem[]>([]);

  readonly total = computed(() => this.mode() === 'server' ? this.serverTotal() : this.clientItems().length);
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / this.size)));
  readonly pageItems = computed(() =>
    this.mode() === 'server' ? this.serverItems()
      : this.clientItems().slice(this.page() * this.size, this.page() * this.size + this.size));

  constructor(private cef: CefService) {}
  ngOnInit(): void { this.reload(); }

  setMode(m: 'server' | 'client'): void { if (m !== this.mode()) { this.mode.set(m); this.page.set(0); this.reload(); } }

  reload(): void {
    this.loading.set(true); this.error.set('');
    const filt = { status: this.status || undefined };
    if (this.mode() === 'client') {
      this.cef.logs({ limit: 1000, ...filt }).subscribe({
        next: r => { this.clientItems.set(r.items); this.loading.set(false); },
        error: () => { this.error.set('Could not load logs (is context-engine :8093 up?).'); this.loading.set(false); }
      });
    } else {
      this.cef.logs({ page: this.page(), size: this.size, ...filt }).subscribe({
        next: r => { this.serverItems.set(r.items); this.serverTotal.set(r.total ?? r.count); this.loading.set(false); },
        error: () => { this.error.set('Could not load logs (is context-engine :8093 up?).'); this.loading.set(false); }
      });
    }
  }

  prev(): void { if (this.page() > 0) { this.page.update(p => p - 1); if (this.mode() === 'server') { this.reload(); } } }
  next(): void { if (this.page() + 1 < this.totalPages()) { this.page.update(p => p + 1); if (this.mode() === 'server') { this.reload(); } } }
}
