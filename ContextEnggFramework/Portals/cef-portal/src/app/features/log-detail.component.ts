import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CefService, CefLogDetail } from '../core/cef.service';
import { FlowDiagramComponent } from '../shared/flow-diagram.component';

/** CEF chat log detail — full "what happened": dynamic pipeline diagram + scope, strategies, tech
 *  stack, db tables, indexes, reasoning engine + vendors, request params and result summary. */
@Component({
  selector: 'cef-log-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FlowDiagramComponent],
  template: `
  <a routerLink="/logs" class="back">‹ All chat logs</a>
  <div *ngIf="error()" class="err">{{ error() }}</div>
  <div *ngIf="loading()" class="muted">Loading…</div>

  <ng-container *ngIf="log() as d">
    <div class="head">
      <h2>{{ d.title }}</h2>
      <p class="desc">{{ d.description }}</p>
      <div class="hmeta">
        <span class="badge">{{ d.status }}</span>
        <span class="m">{{ d.knowledge_base }}</span><span class="m">{{ d.role }}</span>
        <span class="m">{{ d.latency_ms }} ms</span>
        <span class="m">ret {{ d.retrieved }} · used {{ d.used }} · mem {{ d.memory_turns }}</span>
        <span class="m">{{ d.created_dt | date:'medium' }}</span>
      </div>
    </div>

    <section class="card"><h3>🔀 CEF pipeline</h3><cef-flow-diagram [steps]="d.steps"></cef-flow-diagram></section>

    <div class="grid">
      <section class="card"><h3>🧰 Tech stack</h3>
        <table class="kv"><tr *ngFor="let t of d.tech_stack"><td>{{ t.layer }}</td><td>{{ t.tech }}</td></tr></table>
      </section>
      <section class="card"><h3>🗄️ DB tables</h3>
        <table class="kv"><tr *ngFor="let t of d.db_tables"><td>{{ t.name }}</td><td>{{ t.db }} · {{ t.op }}<br><small>{{ t.role }}</small></td></tr></table>
      </section>
      <section class="card"><h3>🧭 Indexes</h3>
        <table class="kv"><tr *ngFor="let i of d.indexes"><td><span class="dot" [class.used]="i.used"></span>{{ i.name }}</td><td>{{ i.type }} <small>{{ i.used ? 'used':'not used' }}</small></td></tr></table>
      </section>
      <section class="card"><h3>🧩 Assembly strategies</h3>
        <div class="chips"><span class="chip" *ngFor="let s of d.strategies">{{ s['name'] }}</span></div>
      </section>
      <section class="card"><h3>🏢 Vendors</h3>
        <ul class="vlist"><li *ngFor="let v of d.vendors" [class.bad]="v.ok===false">
          <div class="vrow"><b>{{ v.name }}</b> <span class="vkind">{{ v.kind }}</span></div>
          <p *ngIf="v.description">{{ v.description }}</p>
        </li></ul>
      </section>
      <section class="card"><h3>🔐 Permission scope</h3><pre>{{ pretty(d.scope) }}</pre></section>
      <section class="card"><h3>⚲ Origin</h3><pre>{{ pretty(d.request_origin) }}</pre></section>
      <section class="card"><h3>⚙️ Request params</h3><pre>{{ pretty(d.request_params) }}</pre></section>
      <section class="card"><h3>📊 Result summary</h3><pre>{{ pretty(d.result_summary) }}</pre></section>
    </div>
  </ng-container>
  `,
  styles: [`
    .back { display:inline-block; margin:.2rem 0 1rem; color:var(--accent); font-weight:700; text-decoration:none; }
    .err { background:#fff1f4; color:#be123c; border:1px solid #fbcfe0; padding:.5rem .7rem; border-radius:8px; }
    .muted { color:var(--muted); text-align:center; padding:1.5rem; }
    .head h2 { margin:0 0 .25rem; font-size:1.3rem; color:var(--ink); }
    .desc { margin:0 0 .5rem; color:var(--muted); }
    .hmeta { display:flex; flex-wrap:wrap; gap:.55rem; align-items:center; margin-bottom:1rem; }
    .hmeta .m { font-size:.76rem; color:var(--muted); }
    .badge { font-size:.66rem; font-weight:800; text-transform:uppercase; padding:.14rem .55rem; border-radius:999px; background:#e7faf1; color:#0f8a5f; }
    .card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; margin-bottom:1rem; box-shadow:var(--shadow); }
    .card h3 { margin:0 0 .6rem; font-size:.95rem; color:var(--ink); }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1rem; }
    table.kv { width:100%; border-collapse:collapse; font-size:.82rem; }
    table.kv td { padding:.3rem .4rem; border-bottom:1px solid #efeafc; vertical-align:top; }
    table.kv td:first-child { color:var(--muted); font-weight:600; width:42%; }
    table.kv small { color:var(--faint,#94a3b8); }
    .chips { display:flex; flex-wrap:wrap; gap:.4rem; }
    .chip { font-size:.72rem; font-weight:600; color:#7c3aed; background:#f1ecfe; border:1px solid #e4d4ff; border-radius:999px; padding:.2rem .6rem; }
    .vlist { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.5rem; }
    .vlist li { border:1px solid var(--line); border-left:4px solid #a855f7; border-radius:10px; padding:.5rem .65rem; background:#faf8ff; }
    .vlist li.bad { border-left-color:#ef4444; background:#fff5f5; }
    .vrow { display:flex; align-items:center; gap:.5rem; } .vrow b { color:var(--ink); }
    .vkind { font-size:.64rem; font-weight:700; text-transform:uppercase; color:#7c3aed; background:#f1ecfe; border-radius:999px; padding:.06rem .45rem; }
    .vlist p { margin:.3rem 0 0; font-size:.8rem; color:var(--muted); line-height:1.45; }
    .dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#d4c8f5; margin-right:.4rem; }
    .dot.used { background:#10b981; }
    pre { margin:0; background:#2a1d52; color:#e9defb; padding:.7rem; border-radius:10px; font-size:.74rem; white-space:pre-wrap; word-break:break-word; }
  `]
})
export class LogDetailComponent implements OnInit {
  readonly log = signal<CefLogDetail | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');

  constructor(private route: ActivatedRoute, private cef: CefService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') || '';
    this.cef.logDetail(id).subscribe({
      next: d => { this.log.set(d); this.loading.set(false); },
      error: () => { this.error.set('Log not found (or context-engine :8093 is down).'); this.loading.set(false); }
    });
  }
  pretty(o: unknown): string { return JSON.stringify(o, null, 2); }
}
