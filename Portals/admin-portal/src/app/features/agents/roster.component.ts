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
          <td><span class="tag" [class.agentic]="r.byFramework[f].service === 'agentic'">{{ serviceLabel(r.byFramework[f].service) }}</span></td>
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

    <!-- how the roster actually works -->
    <section class="vkp-info">
      <h3>What are these, and how are they invoked?</h3>

      <details open class="diagrams-acc">
        <summary>Architecture diagrams</summary>
        <div>
          <p>Visual reference for how a stage runs and how the two services are built. More diagrams
             drop into <code>public/images/arch-diagrams/</code> and are listed here.</p>
          <div class="diagram" *ngFor="let d of diagrams">
            <div class="dtitle">{{ d.title }}</div>
            <div class="ddesc">{{ d.desc }}</div>
            <a [href]="d.src" target="_blank" rel="noopener" [title]="'Open ' + d.title + ' full size'">
              <img [src]="d.src" [alt]="d.title" loading="lazy" />
            </a>
          </div>
        </div>
      </details>

      <details>
        <summary>They are HTTP APIs — not Apache Airflow DAGs</summary>
        <div>
          <p>Each framework is invoked as a <b>synchronous REST call</b> to a FastAPI service — the
             <b>Run</b> button above calls these live. No Airflow is involved on this page.</p>
          <ul>
            <li><b>Service = vehicle-explore-service</b> → <code>POST /api/vehicle-explore/&lt;framework&gt;/&lt;stage&gt;</code>
                (:8090)</li>
            <li><b>Service = agentic-service</b> → <code>POST /agentic/&lt;stage&gt;/&lt;framework&gt;/run</code>
                (:8092)</li>
            <li>This matrix comes from <code>GET /api/vehicle-explore/roster</code> (explore aggregates agentic)</li>
          </ul>
        </div>
      </details>

      <details>
        <summary>The 8 frameworks and where they run</summary>
        <div>
          <p><b>Classic frameworks</b> — hosted in <b>vehicle-explore-service</b> (:8090):
             langgraph · crewai · llamaindex · haystack.</p>
          <p><b>Agent-SDK frameworks</b> — hosted in <b>agentic-service</b> (:8092, isolated venv):
             openai-agents · google-adk · msagent · strands.</p>
          <p>Two services so the heavy modern agent SDKs don't collide with explore's legacy dependency pins.</p>
        </div>
      </details>

      <details>
        <summary>The three stages: collect → index → search</summary>
        <div>
          <ul>
            <li><b>collect</b> — an agent discovers/crawls links from a seed URL, recording the
                <code>company_resource_graph</code>.</li>
            <li><b>index</b> — an agent chunks + embeds content into the shared pgVector table
                (<code>vkp_vectors.vec_*</code>).</li>
            <li><b>search</b> — an agent retrieves the most similar chunks and composes a cited answer.</li>
          </ul>
        </div>
      </details>

      <details>
        <summary>vs the Apache Airflow DAG pipeline (the other path)</summary>
        <div>
          <p>VKP has <b>two</b> ways to run the pipeline:</p>
          <ul>
            <li><b>This page (Agent Roster)</b> — an <b>interactive, single-call API</b> path: run one
                stage with one framework and see the result immediately.</li>
            <li><b>Data Management → Workflows</b> — the <b>orchestrated Airflow DAGs</b>
                (<code>vkp_discover_resources</code>, <code>vkp_process_resources</code>,
                <code>vkp_index_sentence_transformers</code>, <code>vkp_crawl_company_snapshot</code>),
                triggered via <b>airflow-adapter-service</b> (:8083) for the bulk/scheduled pipeline.</li>
          </ul>
          <p>Both write the same stores — they're just different invocation mechanisms (live API vs orchestrated DAG).</p>
        </div>
      </details>
    </section>
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
    .vkp-info { max-width:760px; margin-top:1.75rem; }
    .vkp-info > h3 { margin:0 0 .6rem; }
    .vkp-info details { border:1px solid #eaecf0; border-radius:8px; margin-bottom:.5rem; background:#fff; }
    .vkp-info summary { cursor:pointer; padding:.6rem .85rem; font-weight:600; color:#1f2933; list-style:none; }
    .vkp-info summary::-webkit-details-marker { display:none; }
    .vkp-info summary:before { content:'▸'; margin-right:.5rem; color:#3538cd; }
    .vkp-info details[open] summary:before { content:'▾'; }
    .vkp-info details > div { padding:0 .9rem .8rem; color:#475467; font-size:.88rem; line-height:1.55; }
    .vkp-info details > div p { margin:.4rem 0; }
    .vkp-info ul { margin:.3rem 0; padding-left:1.2rem; }
    .vkp-info code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.82rem; }
    .diagrams-acc { max-width:none; }
    .diagram { margin:1rem 0 1.25rem; }
    .diagram .dtitle { font-weight:700; color:#1f2933; font-size:.95rem; }
    .diagram .ddesc { color:#64748b; font-size:.84rem; margin:.15rem 0 .5rem; }
    .diagram img { width:100%; max-width:1180px; border:1px solid #eaecf0; border-radius:10px; background:#fff;
      box-shadow:0 1px 2px rgba(124,58,237,.08), 0 8px 24px rgba(124,58,237,.08); }
    .diagram a:hover img { border-color:#a855f7; }
  `]
})
export class AgentRosterComponent implements OnInit {
  /** Architecture diagrams shown in the accordion. Add an entry + an SVG under
   *  public/images/arch-diagrams/ to extend (e.g. an index/search sequence per framework). */
  readonly diagrams = [
    { title: 'LangGraph · collect — sequence',
      desc: 'How the Run button drives the collect stage: explore → LangGraph agent → fetch_page tool → website → LLM → links (+ optional persist).',
      src: '/images/arch-diagrams/collect/langgraph-collect.svg' },
    { title: 'vehicle-explore-service — architecture',
      desc: 'The :8090 FastAPI service: search/collect/index APIs, the 4 classic frameworks, retrieval, providers, guardrails, telemetry and stores.',
      src: '/images/arch-diagrams/services/vehicle-explore-service.svg' },
    { title: 'agentic-service — architecture',
      desc: 'The :8092 FastAPI service: the framework registry (8 SDKs) across the collect/index/search stages, in an isolated venv.',
      src: '/images/arch-diagrams/services/agentic-service.svg' },
  ];

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
  /** Friendly name for the hosting service (the raw value still drives run() routing). */
  serviceLabel(s: string): string {
    return s === 'explore' ? 'vehicle-explore-service API' : s === 'agentic' ? 'agentic-service API' : s;
  }

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
