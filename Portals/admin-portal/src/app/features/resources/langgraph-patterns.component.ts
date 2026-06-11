import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Design Patterns → LangGraph. The LangGraph column of agent-patterns-service:
 *  all 10 agentic patterns implemented in LangGraph, verified live, with a link to each cell. */
@Component({
  selector: 'app-langgraph-patterns',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>LangGraph — all 10 agentic patterns</h2>
    <p class="lead">
      The <b>LangGraph column</b> of <code>agent-patterns-service</code> (:8094): every agentic pattern
      implemented in LangGraph, side by side — <b>each verified live</b> end-to-end (gpt-4o-mini). This is
      the "see how the stack's code looks" reference; the same patterns will be filled in for CrewAI,
      LlamaIndex, Haystack, and the agent SDKs (see <a routerLink="/resources/mastery/map">Mastery Map</a>).
    </p>

    <h3>Run it</h3>
    <pre class="code">cd Middleware/agent-patterns-service
pip install -r requirements.txt          # or: uv pip install -r requirements.txt
export OPENAI_API_KEY=...                 # or GROQ_API_KEY=... (free)
uvicorn app.main:app --port 8094

curl -X POST localhost:8094/agent-patterns/<span class="ph">&lt;pattern&gt;</span>/langgraph/run \\
  -H 'content-type: application/json' -d '{{ '{' }}"input":"Does the F-150 tow more than the Tacoma?"{{ '}' }}'</pre>

    <h3>The 10 LangGraph cells</h3>
    <table class="t">
      <thead><tr><th>Pattern</th><th>LangGraph construct</th><th>Verified-live example</th><th>Run · Source</th></tr></thead>
      <tbody>
        <tr *ngFor="let p of patterns">
          <td><b>{{ p.name }}</b></td>
          <td [innerHTML]="p.idiom"></td>
          <td class="ex">{{ p.example }}</td>
          <td class="run">
            <code>{{ p.key }}</code>
            <a class="src" [href]="repo + '/Middleware/agent-patterns-service/app/patterns/' + p.dir + '/langgraph.py'"
               target="_blank" rel="noopener" [title]="p.dir + '/langgraph.py'">&nbsp;↗ code</a>
          </td>
        </tr>
      </tbody>
    </table>

    <p class="foot">
      Service code: <a [href]="repo + '/Middleware/agent-patterns-service'" target="_blank" rel="noopener">agent-patterns-service</a>
      · status matrix: <a [href]="repo + '/Middleware/agent-patterns-service/Development_Tracker.md'" target="_blank" rel="noopener">Development_Tracker.md</a>
      · pattern concepts: <a routerLink="/resources/design-patterns/agentic-patterns">Agentic Patterns</a>.
    </p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1180px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
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
    .t .ex { color:#0f8a5f; font-size:.88rem; }
    .t .run { white-space:nowrap; }
    .src { color:#7c3aed; text-decoration:none; font-weight:700; }
    .src:hover { text-decoration:underline; }
    .arch .foot { color:#475467; font-size:.95rem; margin-top:1rem; }
  `]
})
export class LanggraphPatternsComponent {
  readonly repo = 'https://github.com/javakishore-veleti/Vehicle-Knowledge-Platform/blob/main';

  readonly patterns = [
    { name: 'ReAct', key: 'react', dir: 'react', idiom: '<code>create_react_agent</code> + a <code>vehicle_spec</code> tool (reason → act → observe loop)', example: 'F-150 tows 7,000 lb more than the Tacoma (called the tool twice)' },
    { name: 'Plan-and-Execute', key: 'plan-execute', dir: 'plan_execute', idiom: 'StateGraph: plan → execute (retrieve per sub-query) → synthesize', example: 'decomposed Model 3 vs RAV4 Prime into 4 sub-queries' },
    { name: 'RAG pipeline', key: 'rag', dir: 'rag', idiom: 'StateGraph: retrieve → generate (cited)', example: '"RAV4 Prime range is 42 miles [1]"' },
    { name: 'Router / dispatcher', key: 'router', dir: 'router', idiom: 'classify node + <code>add_conditional_edges</code> to a specialist', example: 'routed → compare specialist' },
    { name: 'Parallelization', key: 'chaining', dir: 'chaining', idiom: 'fan-out 3 perspectives (reducer-merged state) → synthesize', example: 'pros/cons/alternatives merged into one verdict' },
    { name: 'Multi-agent (supervisor)', key: 'multi-agent', dir: 'multi_agent', idiom: 'supervisor + spec/pricing/safety workers → compose', example: 'three specialists → one family-SUV answer' },
    { name: 'Evaluator-optimizer', key: 'evaluator-optimizer', dir: 'evaluator', idiom: 'generate ↔ evaluate loop with a score-gated conditional edge', example: 'score 9 → done in 1 iteration' },
    { name: 'ReWOO', key: 'rewoo', dir: 'rewoo', idiom: 'planner (blind) → worker (no LLM) → solver', example: 'planned 2 tool calls blind → Camry $28,400, Civic $24,650' },
    { name: 'Tree of Thoughts', key: 'tot', dir: 'tot', idiom: 'branch (propose 3) → evaluate (score) → select best', example: 'scored 3 thoughts (10/9/7) → picked the best EV' },
    { name: 'Reflection / Reflexion', key: 'reflection', dir: 'reflection', idiom: 'StateGraph: draft → critique → revise', example: 'draft "42 mi" → critic → revised with EPA detail' },
  ];
}
