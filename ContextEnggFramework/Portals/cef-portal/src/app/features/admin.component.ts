import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CefService, Strategy } from '../core/cef.service';

/** CEF Admin — the context-strategy table + the eval harness (scorecards groundedness). */
@Component({
  selector: 'cef-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <section class="card">
    <div class="card-head">
      <div><h2>Context Strategies</h2><p>The five context-assembly levers per profile.</p></div>
    </div>
    <p class="err" *ngIf="error()">{{ error() }}</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Name</th><th>Budget</th><th>select</th><th>compress</th><th>order</th><th>isolate</th><th>format</th><th>status</th></tr></thead>
        <tbody>
          <tr *ngFor="let s of strategies()">
            <td><b>{{ s.name }}</b><div class="sub">{{ s.description }}</div></td>
            <td class="num">{{ s.charBudget }}</td>
            <td [class.on]="s.selectionEnabled">{{ s.selectionEnabled ? '✓' : '–' }}</td>
            <td [class.on]="s.compressionEnabled">{{ s.compressionEnabled ? '✓' : '–' }}</td>
            <td [class.on]="s.orderingEnabled">{{ s.orderingEnabled ? '✓' : '–' }}</td>
            <td [class.on]="s.isolationEnabled">{{ s.isolationEnabled ? '✓' : '–' }}</td>
            <td [class.on]="s.formatEnabled">{{ s.formatEnabled ? '✓' : '–' }}</td>
            <td><span class="pill">{{ s.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <div class="card-head"><div><h2>Eval Harness</h2><p>Run a golden query through the orchestrator and scorecard its groundedness.</p></div></div>
    <div class="eval">
      <input [(ngModel)]="q" placeholder="golden query…">
      <button (click)="runEval()" [disabled]="busy()">{{ busy() ? '…' : 'Run eval' }}</button>
    </div>
    <div class="score" *ngIf="score() as sc">
      <span class="metric" [class.good]="sc.grounded" [class.bad]="!sc.grounded">grounded: {{ sc.grounded }}</span>
      <span class="metric">citations: {{ sc.citationCount }}</span>
      <span class="metric">sources: {{ sc.sourceCount }}</span>
      <span class="metric">⚡ {{ sc.latencyMs }}ms</span>
    </div>
    <pre *ngIf="answer()">{{ answer() }}</pre>
  </section>
  `,
  styles: [`
    .card { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); padding:1.1rem 1.25rem; margin-bottom:1.1rem; }
    .card-head h2 { margin:0; font-size:1.08rem; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
    .card-head p { margin:.15rem 0 .7rem; color:var(--muted); font-size:.82rem; }
    .err { color:#be123c; background:#fff1f4; border:1px solid #fbcfe0; padding:.5rem .7rem; border-radius:8px; font-size:.85rem; }

    .tablewrap { overflow-x:auto; border:1px solid var(--line); border-radius:12px; }
    table { border-collapse:collapse; width:100%; font-size:.88rem; }
    th, td { padding:.55rem .7rem; text-align:left; border-bottom:1px solid var(--line); }
    thead th { background:#f6f1ff; color:var(--accent); font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; }
    tbody tr:last-child td { border-bottom:none; }
    tbody tr:hover { background:#faf8ff; }
    td.num { font-variant-numeric:tabular-nums; color:var(--muted); }
    td.on { color:#10b981; font-weight:800; text-align:center; }
    td:not(.on):not(.num) { text-align:left; }
    .sub { color:var(--muted); font-size:.76rem; }
    .pill { font-size:.7rem; font-weight:700; color:#0f8a5f; background:#e7faf1; border:1px solid #c5f0db; padding:.1rem .5rem; border-radius:999px; }

    .eval { display:flex; gap:.6rem; }
    .eval input { flex:1; padding:.6rem .8rem; border:1px solid var(--line); border-radius:10px; font-size:.9rem; }
    .eval input:focus { outline:none; border-color:var(--accent2); box-shadow:0 0 0 3px rgba(168,85,247,.18); }
    .eval button { padding:.6rem 1.2rem; background:var(--grad); color:#fff; border:none; border-radius:10px; font-weight:700; cursor:pointer; box-shadow:0 6px 16px rgba(124,58,237,.3); }
    .eval button:disabled { opacity:.55; }
    .score { margin-top:.7rem; display:flex; flex-wrap:wrap; gap:.4rem; }
    .metric { font-size:.78rem; font-weight:600; color:var(--accent); background:var(--accent-soft); border:1px solid #e9defb; border-radius:999px; padding:.2rem .65rem; }
    .metric.good { background:#e7faf1; color:#0f8a5f; border-color:#c5f0db; }
    .metric.bad { background:#fff1f4; color:#be123c; border-color:#fbcfe0; }
    pre { background:#2a1d52; color:#e9defb; padding:.8rem; border-radius:10px; font-size:.8rem; white-space:pre-wrap; margin-top:.7rem; }
  `]
})
export class AdminComponent implements OnInit {
  readonly strategies = signal<Strategy[]>([]);
  readonly error = signal('');
  readonly score = signal<any | null>(null);
  readonly answer = signal('');
  readonly busy = signal(false);
  q = 'What hybrid SUVs does Toyota offer?';

  constructor(private cef: CefService) {}

  ngOnInit(): void {
    this.cef.strategies().subscribe({
      next: s => this.strategies.set(s),
      error: () => this.error.set('Could not load strategies — is context-admin (:8094) running?')
    });
  }

  runEval(): void {
    const query = this.q.trim(); if (!query) { return; }
    this.busy.set(true); this.score.set(null); this.answer.set('');
    this.cef.evalRun({ query, companyId: '10000000-0000-4000-8000-000000000004' }).subscribe({
      next: d => { this.score.set(d.scorecard); this.answer.set(d.answer || JSON.stringify(d, null, 2)); this.busy.set(false); },
      error: e => { this.error.set('Eval error: ' + (e?.error?.detail ?? e?.message ?? e)); this.busy.set(false); }
    });
  }
}
