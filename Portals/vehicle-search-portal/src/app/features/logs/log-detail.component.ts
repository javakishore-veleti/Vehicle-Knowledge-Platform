import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ExploreService, LogDetail } from '../../core/explore.service';
import { FlowDiagramComponent } from '../../shared/flow-diagram.component';

/** Log detail — full "what happened" for one search: dynamic flow diagram + tech stack, db tables,
 *  indexes, LLMs, 3rd-party vendors, guardrails, request params and result summary. */
@Component({
  selector: 'vs-log-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FlowDiagramComponent],
  template: `
  <a routerLink="/logs" class="back">‹ All logs</a>
  <div *ngIf="error()" class="vs-error">{{ error() }}</div>
  <div *ngIf="loading()" class="vs-skeleton">Loading…</div>

  <ng-container *ngIf="log() as d">
    <div class="head">
      <h1>{{ d.title }}</h1>
      <p class="desc">{{ d.description }}</p>
      <div class="hmeta">
        <span class="badge" [attr.data-st]="d.status">{{ d.status }}</span>
        <span class="m">{{ d.latency_ms }} ms</span>
        <span class="m">{{ d.result_count }} sources</span>
        <span class="m">{{ d.created_dt | date:'medium' }}</span>
        <span class="m">id {{ d.id }}</span>
      </div>
    </div>

    <section class="card">
      <h2>🔀 Request flow</h2>
      <vs-flow-diagram [steps]="d.steps"></vs-flow-diagram>
    </section>

    <div class="grid">
      <section class="card">
        <h2>🧰 Tech stack</h2>
        <table class="kv"><tr *ngFor="let t of d.tech_stack"><td>{{ t.layer }}</td><td>{{ t.tech }}</td></tr></table>
      </section>

      <section class="card">
        <h2>🗄️ DB tables</h2>
        <table class="kv"><tr *ngFor="let t of d.db_tables"><td>{{ t.name }}</td><td>{{ t.db }} · {{ t.op }}<br><small>{{ t.role }}</small></td></tr></table>
      </section>

      <section class="card">
        <h2>🧭 Indexes</h2>
        <table class="kv"><tr *ngFor="let i of d.indexes"><td><span class="dot" [class.used]="i.used"></span>{{ i.name }}</td><td>{{ i.type }} <small>{{ i.used ? 'used' : 'not used' }}</small></td></tr></table>
      </section>

      <section class="card">
        <h2>🏢 3rd-party vendors</h2>
        <ul class="vlist">
          <li *ngFor="let v of d.vendors" [class.bad]="v.ok===false">
            <div class="vrow"><b>{{ v.name }}</b> <span class="vkind">{{ v.kind }}</span>
              <span class="vok" [class.no]="v.ok===false">{{ v.ok===false ? 'failed' : 'ok' }}</span></div>
            <p *ngIf="v.description">{{ v.description }}</p>
            <small *ngIf="v.role">role: {{ v.role }}</small>
          </li>
        </ul>
      </section>

      <section class="card" *ngIf="d.llms?.length">
        <h2>🤖 LLMs invoked</h2>
        <p class="cap">Invoked <b>after retrieval</b> — all selected providers run <b>in parallel</b> over the
          same retrieved sources (a fan-out so you can compare answers/latency/cost side by side).</p>
        <table class="grid-tbl">
          <thead><tr><th>provider</th><th>model</th><th>ok</th><th>tokens</th><th>cost</th><th>ms</th><th>when</th></tr></thead>
          <tbody><tr *ngFor="let l of d.llms">
            <td>{{ l['label'] || l['provider'] }}</td><td>{{ l['model'] }}</td>
            <td>{{ l['ok'] ? '✓' : '✗' }}</td><td>{{ l['totalTokens'] || '–' }}</td>
            <td>{{ l['costUsd'] != null ? ('$'+l['costUsd']) : '–' }}</td><td>{{ l['latencyMs'] || '–' }}</td>
            <td><small>{{ l['whenInvoked'] || 'after retrieval' }}</small></td>
          </tr></tbody>
        </table>
      </section>

      <section class="card">
        <h2>⚲ Origin</h2>
        <pre>{{ pretty(d.request_origin) }}</pre>
      </section>

      <section class="card">
        <h2>⚙️ Request params</h2>
        <pre>{{ pretty(d.request_params) }}</pre>
      </section>

      <section class="card">
        <h2>📊 Result summary</h2>
        <pre>{{ pretty(d.result_summary) }}</pre>
      </section>
    </div>
  </ng-container>
  `,
  styles: [`
    .back { display:inline-block; margin:.2rem 0 1rem; color:var(--vs-brand); font-weight:700; text-decoration:none; }
    .head h1 { margin:0 0 .25rem; font-size:1.35rem; color:var(--vs-text); }
    .desc { margin:0 0 .5rem; color:var(--vs-muted); }
    .hmeta { display:flex; flex-wrap:wrap; gap:.55rem; align-items:center; margin-bottom:1rem; }
    .hmeta .m { font-size:.76rem; color:var(--vs-muted); }
    .badge { font-size:.66rem; font-weight:800; text-transform:uppercase; padding:.14rem .55rem; border-radius:999px; background:#f1ecfe; color:#7c3aed; }
    .badge[data-st=blocked], .badge[data-st=none] { background:#fde8e8; color:#c0392b; }
    .badge[data-st=llm] { background:#e7faf1; color:#0f8a5f; }
    .card { background:#fff; border:1px solid var(--vs-border); border-radius:14px; padding:1rem 1.1rem; margin-bottom:1rem; box-shadow:0 1px 2px rgba(124,58,237,.08), 0 10px 26px rgba(124,58,237,.08); }
    .card h2 { margin:0 0 .6rem; font-size:.95rem; color:var(--vs-text); }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1rem; }
    table.kv { width:100%; border-collapse:collapse; font-size:.82rem; }
    table.kv td { padding:.3rem .4rem; border-bottom:1px solid #efeafc; vertical-align:top; }
    table.kv td:first-child { color:var(--vs-muted); font-weight:600; width:42%; }
    table.kv small { color:var(--vs-faint,#94a3b8); }
    .grid-tbl { width:100%; border-collapse:collapse; font-size:.78rem; }
    .grid-tbl th { text-align:left; color:#7c3aed; font-size:.66rem; text-transform:uppercase; border-bottom:1px solid var(--vs-border); padding:.3rem .4rem; }
    .grid-tbl td { padding:.3rem .4rem; border-bottom:1px solid #efeafc; }
    .chips { display:flex; flex-wrap:wrap; gap:.4rem; }
    .chip { font-size:.74rem; font-weight:600; color:#7c3aed; background:#f1ecfe; border:1px solid #e4d4ff; border-radius:999px; padding:.2rem .6rem; }
    .chip.bad { color:#c0392b; background:#fde8e8; border-color:#f8c4c4; }
    .chip small { color:var(--vs-muted); font-weight:500; }
    .vlist { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.6rem; }
    .vlist li { border:1px solid var(--vs-border); border-left:4px solid #a855f7; border-radius:10px; padding:.55rem .7rem; background:#faf8ff; }
    .vlist li.bad { border-left-color:#ef4444; background:#fff5f5; }
    .vrow { display:flex; align-items:center; gap:.5rem; }
    .vrow b { color:var(--vs-text); }
    .vkind { font-size:.66rem; font-weight:700; text-transform:uppercase; color:#7c3aed; background:#f1ecfe; border-radius:999px; padding:.06rem .45rem; }
    .vok { margin-left:auto; font-size:.64rem; font-weight:800; text-transform:uppercase; color:#0f8a5f; background:#e7faf1; border-radius:999px; padding:.06rem .45rem; }
    .vok.no { color:#c0392b; background:#fde8e8; }
    .vlist p { margin:.35rem 0 .2rem; font-size:.8rem; color:var(--vs-muted); line-height:1.45; }
    .vlist small { color:var(--vs-faint,#94a3b8); font-size:.72rem; }
    .cap { margin:0 0 .6rem; font-size:.8rem; color:var(--vs-muted); line-height:1.45; }
    .dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#d4c8f5; margin-right:.4rem; }
    .dot.used { background:#10b981; }
    pre { margin:0; background:#2a1d52; color:#e9defb; padding:.7rem; border-radius:10px; font-size:.74rem; white-space:pre-wrap; word-break:break-word; }
  `]
})
export class LogDetailComponent implements OnInit {
  readonly log = signal<LogDetail | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');

  constructor(private route: ActivatedRoute, private explore: ExploreService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') || '';
    this.explore.logDetail(id).subscribe({
      next: d => { this.log.set(d); this.loading.set(false); },
      error: () => { this.error.set('Log not found (or vehicle-explore-service :8090 is down).'); this.loading.set(false); }
    });
  }

  pretty(o: unknown): string { return JSON.stringify(o, null, 2); }
}
