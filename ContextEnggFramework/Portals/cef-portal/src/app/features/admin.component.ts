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
  <h2>Context Strategies</h2>
  <p class="err" *ngIf="error()">{{ error() }}</p>
  <table>
    <thead><tr><th>Name</th><th>Budget</th><th>select</th><th>compress</th><th>order</th><th>isolate</th><th>format</th><th>status</th></tr></thead>
    <tbody>
      <tr *ngFor="let s of strategies()">
        <td><b>{{ s.name }}</b><div class="sub">{{ s.description }}</div></td>
        <td>{{ s.charBudget }}</td>
        <td [class.on]="s.selectionEnabled">{{ s.selectionEnabled ? '✓' : '—' }}</td>
        <td [class.on]="s.compressionEnabled">{{ s.compressionEnabled ? '✓' : '—' }}</td>
        <td [class.on]="s.orderingEnabled">{{ s.orderingEnabled ? '✓' : '—' }}</td>
        <td [class.on]="s.isolationEnabled">{{ s.isolationEnabled ? '✓' : '—' }}</td>
        <td [class.on]="s.formatEnabled">{{ s.formatEnabled ? '✓' : '—' }}</td>
        <td>{{ s.status }}</td>
      </tr>
    </tbody>
  </table>

  <h2>Eval Harness</h2>
  <div class="eval">
    <input [(ngModel)]="q" placeholder="golden query…">
    <button (click)="runEval()" [disabled]="busy()">{{ busy() ? '…' : 'Run eval' }}</button>
    <div class="score" *ngIf="score() as sc">
      <span [class.good]="sc.grounded" [class.bad]="!sc.grounded">grounded: {{ sc.grounded }}</span>
      <span>citations: {{ sc.citationCount }}</span><span>sources: {{ sc.sourceCount }}</span><span>{{ sc.latencyMs }}ms</span>
    </div>
    <pre *ngIf="answer()">{{ answer() }}</pre>
  </div>
  `,
  styles: [`
    h2 { margin:1rem 0 .5rem; } .err { color:#b42318; }
    table { border-collapse:collapse; width:100%; background:#fff; font-size:.9rem; }
    th,td { border:1px solid var(--line); padding:.4rem .6rem; text-align:left; } th { background:#f9fafb; }
    td.on { color:#16a34a; } .sub { color:var(--muted); font-size:.78rem; }
    .eval { background:#fff; border:1px solid var(--line); border-radius:10px; padding:1rem; }
    .eval input { padding:.5rem; border:1px solid #d0d5dd; border-radius:6px; width:60%; }
    .eval button { padding:.5rem 1rem; background:var(--accent); color:#fff; border:none; border-radius:6px; cursor:pointer; }
    .score { margin-top:.6rem; } .score span { display:inline-block; background:#f2f4f7; border-radius:8px; padding:.2rem .6rem; margin:.2rem .3rem 0 0; font-size:.82rem; }
    .score .good { background:#ecfdf3; color:#067647; } .score .bad { background:#fef3f2; color:#b42318; }
    pre { background:#0c111d; color:#d1e0ff; padding:.7rem; border-radius:8px; font-size:.8rem; white-space:pre-wrap; margin-top:.5rem; }
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
