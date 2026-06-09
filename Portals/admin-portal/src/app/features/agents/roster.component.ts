import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgentRosterService, Roster } from '../../core/agent-roster.service';

/** Agent Roster — the full agent-framework roster (classic + new SDKs) across all three stages,
 *  with a panel to run any stage against any framework. */
@Component({
  selector: 'app-agent-roster',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <div class="vkp-page">
    <h2>Agent Roster</h2>
    <p class="vkp-sub" *ngIf="roster() as r">
      {{ r.frameworkCount }} frameworks · collect / index / search ·
      <span [class.ok]="r.services.agenticReachable" [class.warn]="!r.services.agenticReachable">
        agentic-service {{ r.services.agenticReachable ? 'reachable' : 'unreachable' }}
      </span>
    </p>
    <p class="vkp-err" *ngIf="error()">{{ error() }}</p>

    <!-- coverage matrix -->
    <table class="vkp-matrix" *ngIf="roster() as r">
      <thead><tr><th>Framework</th><th>Service</th><th *ngFor="let s of stages">{{ s }}</th></tr></thead>
      <tbody>
        <tr *ngFor="let f of frameworks()">
          <td class="fw">{{ f }}</td>
          <td><span class="tag" [class.agentic]="r.byFramework[f].service === 'agentic'">{{ r.byFramework[f].service }}</span></td>
          <td *ngFor="let s of stages" class="cell">
            <i class="pi" [class.pi-check-circle]="has(f, s)" [class.pi-minus]="!has(f, s)"
               [class.yes]="has(f, s)"></i>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- run a stage -->
    <div class="vkp-run" *ngIf="roster() as r">
      <h3>Run a stage</h3>
      <div class="row">
        <label>Stage
          <select [(ngModel)]="stage"><option *ngFor="let s of stages">{{ s }}</option></select>
        </label>
        <label>Framework
          <select [(ngModel)]="framework">
            <option *ngFor="let f of frameworksFor(stage)" [value]="f">{{ f }}</option>
          </select>
        </label>
        <button (click)="run()" [disabled]="busy()">{{ busy() ? 'Running…' : 'Run' }}</button>
      </div>
      <label class="full" *ngIf="stage === 'search'">Query
        <input [(ngModel)]="query" placeholder="What hybrid SUVs does Toyota offer?" />
      </label>
      <label class="full" *ngIf="stage === 'collect'">Seed URL
        <input [(ngModel)]="seedUrl" placeholder="https://www.toyota.com/" />
      </label>
      <label class="full" *ngIf="stage === 'index'">Content
        <textarea [(ngModel)]="content" rows="4" placeholder="Paste vehicle content to chunk + index…"></textarea>
      </label>
      <pre class="vkp-result" *ngIf="result()">{{ result() }}</pre>
    </div>
  </div>
  `,
  styles: [`
    .vkp-page { padding: 1rem 1.25rem; }
    .vkp-sub { color:#667085; margin-top:-.4rem; } .ok{color:#16a34a;} .warn{color:#d97706;}
    .vkp-err { color:#b42318; }
    .vkp-matrix { border-collapse:collapse; width:100%; max-width:760px; margin:.75rem 0 1.5rem; font-size:.92rem; }
    .vkp-matrix th, .vkp-matrix td { border:1px solid #eaecf0; padding:.4rem .6rem; text-align:left; }
    .vkp-matrix thead th { background:#f9fafb; }
    .vkp-matrix .fw { font-weight:600; } .vkp-matrix .cell { text-align:center; }
    .vkp-matrix .pi.yes { color:#16a34a; } .vkp-matrix .pi-minus { color:#d0d5dd; }
    .tag { background:#eef2ff; color:#3538cd; border-radius:10px; padding:.1rem .5rem; font-size:.78rem; }
    .tag.agentic { background:#ecfdf3; color:#067647; }
    .vkp-run { max-width:760px; } .vkp-run .row { display:flex; gap:1rem; align-items:flex-end; margin-bottom:.6rem; }
    .vkp-run label { display:flex; flex-direction:column; font-size:.82rem; color:#475467; gap:.2rem; }
    .vkp-run label.full { margin:.4rem 0; } .vkp-run input, .vkp-run textarea, .vkp-run select { padding:.4rem; border:1px solid #d0d5dd; border-radius:6px; }
    .vkp-run label.full input, .vkp-run label.full textarea { width:100%; }
    .vkp-run button { padding:.45rem 1rem; background:#3538cd; color:#fff; border:none; border-radius:6px; cursor:pointer; }
    .vkp-run button:disabled { opacity:.6; cursor:default; }
    .vkp-result { background:#0c111d; color:#d1e0ff; padding:.75rem; border-radius:8px; overflow:auto; max-height:340px; font-size:.8rem; }
  `]
})
export class AgentRosterComponent implements OnInit {
  readonly roster = signal<Roster | null>(null);
  readonly error = signal<string>('');
  readonly result = signal<string>('');
  readonly busy = signal<boolean>(false);
  readonly stages = ['collect', 'index', 'search'];

  stage = 'collect';
  framework = '';
  query = 'What hybrid SUVs does Toyota offer?';
  seedUrl = 'https://www.toyota.com/';
  content = '';

  constructor(private svc: AgentRosterService) {}

  ngOnInit(): void {
    this.svc.roster().subscribe({
      next: r => { this.roster.set(r); this.framework = this.frameworksFor(this.stage)[0] ?? ''; },
      error: () => this.error.set('Could not load the roster — is the explore service (:8090) running?')
    });
  }

  frameworks(): string[] { return Object.keys(this.roster()?.byFramework ?? {}); }
  frameworksFor(stage: string): string[] { return this.roster()?.matrix?.[stage] ?? []; }
  has(f: string, s: string): boolean { return (this.roster()?.byFramework?.[f]?.stages ?? []).includes(s); }

  run(): void {
    const r = this.roster(); if (!r || !this.framework) { return; }
    const service = r.byFramework[this.framework].service;
    const body: Record<string, unknown> =
      this.stage === 'search' ? { query: this.query, useLlm: false }
      : this.stage === 'collect' ? { seedUrl: this.seedUrl }
      : { content: this.content };
    this.busy.set(true); this.result.set('');
    this.svc.run(this.stage, this.framework, service, body).subscribe({
      next: res => { this.busy.set(false); this.result.set(JSON.stringify(res, null, 2)); },
      error: e => { this.busy.set(false); this.result.set('Error: ' + (e?.error?.detail ?? e?.message ?? e)); }
    });
  }
}
