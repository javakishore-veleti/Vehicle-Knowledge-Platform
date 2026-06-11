import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';

interface Row { name: string; key: string; dir: string; idiom: string; example: string; }
interface FW { name: string; file: string; blurb: string; rows: Row[]; }

/** Resources → Design Patterns → <Framework>. One reusable, data-driven page: all 10 agentic patterns
 *  implemented in the framework given by the route's `fw` data, each linking to its cell on GitHub. */
@Component({
  selector: 'app-framework-patterns',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch" *ngIf="fw">
    <h2>{{ fw.name }} — all 10 agentic patterns</h2>
    <p class="lead" [innerHTML]="fw.blurb"></p>

    <h3>Run it</h3>
    <pre class="code">cd Middleware/agent-patterns-service
uv pip install -r requirements.txt        # or: pip install -r requirements.txt   (Python 3.12)
export OPENAI_API_KEY=...                  # or GROQ_API_KEY=... (free)
uvicorn app.main:app --port 8094

curl -X POST localhost:8094/agent-patterns/<span class="ph">&lt;pattern&gt;</span>/{{ fwKey }}/run \\
  -H 'content-type: application/json' -d '{{ '{' }}"input":"Does the F-150 tow more than the Tacoma?"{{ '}' }}'</pre>

    <h3>The 10 {{ fw.name }} cells <span class="dim">(all verified live)</span></h3>
    <table class="t">
      <thead><tr><th>Pattern</th><th>{{ fw.name }} construct</th><th>Verified-live example</th><th>Run · Source</th></tr></thead>
      <tbody>
        <tr *ngFor="let p of fw.rows">
          <td><b>{{ p.name }}</b></td>
          <td [innerHTML]="p.idiom"></td>
          <td class="ex">{{ p.example }}</td>
          <td class="run"><code>{{ p.key }}</code>
            <a class="src" [href]="repo + '/Middleware/agent-patterns-service/app/patterns/' + p.dir + '/' + fw.file + '.py'"
               target="_blank" rel="noopener" [title]="p.dir + '/' + fw.file + '.py'">&nbsp;↗ code</a></td>
        </tr>
      </tbody>
    </table>

    <p class="foot">
      Service: <a [href]="repo + '/Middleware/agent-patterns-service'" target="_blank" rel="noopener">agent-patterns-service</a>
      · matrix: <a [href]="repo + '/Middleware/agent-patterns-service/Development_Tracker.md'" target="_blank" rel="noopener">Development_Tracker.md</a>
      · concepts: <a routerLink="/resources/design-patterns/agentic-patterns">Agentic Patterns</a>
      · progress: <a routerLink="/resources/mastery/map">Mastery Map</a>.
    </p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1180px; }
    .arch h2 { margin: 0 0 .4rem; } .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .dim { color:#94a3b8; font-weight:400; font-size:.9rem; }
    .arch .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.9rem; }
    .arch a { color:#3538cd; }
    .code { background:#0c111d; color:#d1e0ff; padding:.85rem; border-radius:8px; font-size:.82rem; white-space:pre-wrap; line-height:1.55; overflow-x:auto; }
    .code .ph { color:#fbbf24; }
    .t { border-collapse:collapse; width:100%; font-size:.93rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.55rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; }
    .t .ex { color:#0f8a5f; font-size:.88rem; } .t .run { white-space:nowrap; }
    .src { color:#7c3aed; text-decoration:none; font-weight:700; } .src:hover { text-decoration:underline; }
    .arch .foot { color:#475467; font-size:.95rem; margin-top:1rem; }
  `]
})
export class FrameworkPatternsComponent implements OnInit {
  readonly repo = 'https://github.com/javakishore-veleti/Vehicle-Knowledge-Platform/blob/main';
  fw!: FW;
  fwKey = 'langgraph';

  constructor(private route: ActivatedRoute) {}
  ngOnInit(): void {
    this.fwKey = this.route.snapshot.data['fw'] || 'langgraph';
    this.fw = FRAMEWORKS[this.fwKey];
  }
}

const ROWS = {
  react: { name: 'ReAct', key: 'react', dir: 'react' },
  plan: { name: 'Plan-and-Execute', key: 'plan-execute', dir: 'plan_execute' },
  rag: { name: 'RAG pipeline', key: 'rag', dir: 'rag' },
  router: { name: 'Router / dispatcher', key: 'router', dir: 'router' },
  chain: { name: 'Parallelization', key: 'chaining', dir: 'chaining' },
  multi: { name: 'Multi-agent (supervisor)', key: 'multi-agent', dir: 'multi_agent' },
  eval: { name: 'Evaluator-optimizer', key: 'evaluator-optimizer', dir: 'evaluator' },
  rewoo: { name: 'ReWOO', key: 'rewoo', dir: 'rewoo' },
  tot: { name: 'Tree of Thoughts', key: 'tot', dir: 'tot' },
  reflect: { name: 'Reflection / Reflexion', key: 'reflection', dir: 'reflection' },
};

const FRAMEWORKS: Record<string, FW> = {
  langgraph: {
    name: 'LangGraph', file: 'langgraph',
    blurb: 'The <b>LangGraph column</b> of <code>agent-patterns-service</code> (:8094): every agentic pattern as a LangGraph graph, each verified live end-to-end. See the <a routerLink="/resources/mastery/map">Mastery Map</a> for the full framework matrix.',
    rows: [
      { ...ROWS.react, idiom: '<code>create_react_agent</code> + a <code>vehicle_spec</code> tool', example: 'F-150 tows 7,000 lb more than the Tacoma' },
      { ...ROWS.plan, idiom: 'StateGraph: plan → execute (retrieve) → synthesize', example: 'decomposed Model 3 vs RAV4 Prime into 4 sub-queries' },
      { ...ROWS.rag, idiom: 'StateGraph: retrieve → generate (cited)', example: '"RAV4 Prime range is 42 miles [1]"' },
      { ...ROWS.router, idiom: 'classify node + <code>add_conditional_edges</code>', example: 'routed → compare specialist' },
      { ...ROWS.chain, idiom: 'fan-out 3 perspectives (reducer-merged state) → synthesize', example: 'pros/cons/alts merged into one verdict' },
      { ...ROWS.multi, idiom: 'supervisor + spec/pricing/safety workers → compose', example: 'three specialists → one family-SUV answer' },
      { ...ROWS.eval, idiom: 'generate ↔ evaluate loop with a score-gated edge', example: 'score 9 → done in 1 iteration' },
      { ...ROWS.rewoo, idiom: 'planner (blind) → worker (no LLM) → solver', example: 'planned 2 calls blind → Camry $28,400, Civic $24,650' },
      { ...ROWS.tot, idiom: 'branch (propose 3) → evaluate (score) → select', example: 'scored 3 thoughts (10/9/7) → best EV' },
      { ...ROWS.reflect, idiom: 'StateGraph: draft → critique → revise', example: 'draft "42 mi" → critic → revised with EPA detail' },
    ],
  },
  crewai: {
    name: 'CrewAI', file: 'crewai',
    blurb: 'The <b>CrewAI column</b> of <code>agent-patterns-service</code> (:8094): every pattern expressed as CrewAI agents + tasks + crews, each verified live. CrewAI shines on the multi-agent pattern (its native crew).',
    rows: [
      { ...ROWS.react, idiom: 'an <code>Agent</code> + <code>&#64;tool</code> <code>vehicle_spec</code> (agent loop)', example: 'F-150 13,500 lb vs Tacoma 6,500 lb' },
      { ...ROWS.plan, idiom: 'planner Agent → Python retrieve → synthesizer Agent', example: 'decomposed Model 3 vs RAV4 into 4 sub-queries' },
      { ...ROWS.rag, idiom: 'Agent + <code>search_docs</code> tool, cited answer', example: '"RAV4 Prime range is 42 miles [1]"' },
      { ...ROWS.router, idiom: 'classifier Agent → delegated specialist Agent', example: 'routed → compare' },
      { ...ROWS.chain, idiom: 'async pros/cons/alts on separate agents → lead merge (context)', example: 'balanced Model 3 verdict' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety specialists + lead — native crew', example: 'composed family-SUV answer (25s)' },
      { ...ROWS.eval, idiom: 'writer + judge + revise Tasks chained via <code>context</code>', example: 'MPG answer scored + refined' },
      { ...ROWS.rewoo, idiom: 'planner Agent (blind) → Python execute → solver Agent', example: 'Camry $28,400, Civic $24,650' },
      { ...ROWS.tot, idiom: 'proposer Agent (3) → evaluator Agent scores → select', example: 'scored 3 → picked best EV' },
      { ...ROWS.reflect, idiom: 'writer + critic agents, sequential crew (context)', example: 'draft → critique → refined RAV4 answer' },
    ],
  },
};
