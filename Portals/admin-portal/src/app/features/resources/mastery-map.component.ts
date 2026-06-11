import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Mastery → Map. The control panel for using VKP as an agentic-AI mastery lab:
 *  a status matrix of every domain + the ordered roadmap. Updated as each cycle ships. */
@Component({
  selector: 'app-mastery-map',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Agentic AI — Mastery Map <span class="dim">(VKP as the lab)</span></h2>
    <p class="lead">
      One source of truth for mastering the whole agentic-AI stack <i>by building it</i> in this repo:
      every domain with its <b>status</b>, <b>where it lives</b>, and the <b>next step</b>, plus the ordered
      roadmap. Each <b>cycle</b> ships three things for one domain — a learning page, a real working
      implementation wired into the services / <a routerLink="/agents/roster">Agent Roster</a>, and a demo.
    </p>

    <nav class="toc">
      <div class="toc-title">Contents</div>
      <ol>
        <li><a (click)="go('s-progress')">Progress</a></li>
        <li><a (click)="go('s-matrix')">Status matrix (every domain)</a></li>
        <li><a (click)="go('s-roadmap')">Roadmap (build order)</a></li>
      </ol>
    </nav>

    <h3 id="s-progress">Progress</h3>
    <div class="prog">
      <div class="pill built"><b>{{ count('built') }}</b> built</div>
      <div class="pill partial"><b>{{ count('partial') }}</b> partial</div>
      <div class="pill planned"><b>{{ count('planned') }}</b> planned</div>
      <div class="pill total"><b>{{ domains.length }}</b> domains</div>
    </div>

    <h3 id="s-matrix">Status matrix — every domain</h3>
    <table class="t">
      <thead><tr><th>Area</th><th>Domain</th><th>Status</th><th>Where it lives</th><th>Next step</th></tr></thead>
      <tbody>
        <tr *ngFor="let d of domains">
          <td>{{ d.area }}</td>
          <td><b>{{ d.domain }}</b></td>
          <td><span class="st" [ngClass]="d.status">{{ stLabel(d.status) }}</span></td>
          <td><span [innerHTML]="d.where"></span><a *ngIf="d.src" class="src" [href]="repo + '/' + d.src"
              target="_blank" rel="noopener" [title]="d.src">&nbsp;↗</a></td>
          <td [innerHTML]="d.next"></td>
        </tr>
      </tbody>
    </table>

    <h3 id="s-roadmap">Roadmap — build order</h3>
    <p>Reorderable; each step is one (sometimes two) cycle. <span class="st next">▶ next</span> is what we
       build now.</p>
    <ol class="road">
      <li *ngFor="let r of roadmap" [class.next]="r.state === 'next'" [class.done]="r.state === 'done'">
        <span class="road-name"><b>{{ r.name }}</b>
          <span *ngIf="r.state === 'next'" class="st next">▶ next</span>
          <span *ngIf="r.state === 'done'" class="st built">✅ done</span></span>
        <span class="road-why" [innerHTML]="r.why"></span>
      </li>
    </ol>

    <p class="foot">See the <a routerLink="/resources/design-patterns/agentic-patterns">Agentic Patterns</a>
       page for the pattern-level detail (50 VKP use cases) that feeds the first roadmap step.</p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1180px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .dim { color:#94a3b8; font-weight:400; font-size:.9rem; }
    .arch .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.9rem; }
    .arch a { color:#3538cd; }
    .toc { background:#faf8ff; border:1px solid #e9e3fb; border-left:3px solid #7c3aed; border-radius:8px;
      padding:.7rem 1rem .8rem; margin:1rem 0 1.5rem; max-width:520px; }
    .toc-title { font-size:.74rem; letter-spacing:.08em; text-transform:uppercase; font-weight:700; color:#7b74a8; margin-bottom:.45rem; }
    .toc ol { margin:0; padding-left:1.4rem; } .toc li { margin:.28rem 0; font-size:.96rem; }
    .toc li::marker { color:#a855f7; font-weight:700; }
    .toc a { color:#3538cd; cursor:pointer; text-decoration:none; } .toc a:hover { text-decoration:underline; }
    .prog { display:flex; flex-wrap:wrap; gap:.6rem; margin:.4rem 0 .5rem; }
    .pill { border-radius:20px; padding:.3rem .9rem; font-size:.92rem; border:1px solid; }
    .pill b { font-size:1.05rem; }
    .pill.built { background:#ecfdf3; color:#0f8a5f; border-color:#b7f0d2; }
    .pill.partial { background:#fff7ed; color:#b45309; border-color:#fde0b0; }
    .pill.planned { background:#f1f5f9; color:#475569; border-color:#e2e8f0; }
    .pill.total { background:#f6f1ff; color:#4c1d95; border-color:#e9e3fb; }
    .t { border-collapse:collapse; width:100%; font-size:.92rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.5rem .65rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; color:#7b74a8; font-size:.85rem; }
    .src { color:#7c3aed; text-decoration:none; font-weight:700; }
    .st { border-radius:10px; padding:.05rem .5rem; font-size:.78rem; font-weight:700; white-space:nowrap; }
    .st.built { background:#ecfdf3; color:#0f8a5f; border:1px solid #b7f0d2; }
    .st.partial { background:#fff7ed; color:#b45309; border:1px solid #fde0b0; }
    .st.planned { background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; }
    .st.next { background:#eef2ff; color:#3538cd; border:1px solid #c7d2fe; margin-left:.4rem; }
    .road { padding-left:1.4rem; }
    .road li { margin:.4rem 0; color:#344054; font-size:.96rem; line-height:1.5; }
    .road li::marker { color:#a855f7; font-weight:700; }
    .road li.next { background:#f7f9ff; border-left:3px solid #3538cd; border-radius:6px; padding:.25rem .6rem; list-style-position:inside; }
    .road-name { font-size:1rem; } .road-why { display:block; color:#475467; font-size:.92rem; }
    .arch .foot { color:#475467; font-size:.95rem; margin-top:1rem; }
  `]
})
export class MasteryMapComponent {
  readonly repo = 'https://github.com/javakishore-veleti/Vehicle-Knowledge-Platform/blob/main';

  go(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  stLabel(s: string): string {
    return s === 'built' ? '✅ built' : s === 'partial' ? '◑ partial' : '○ planned';
  }
  count(s: string): number {
    return this.domains.filter(d => d.status === s).length;
  }

  readonly domains = [
    { area: 'Patterns', domain: 'Agentic patterns (10)', status: 'partial', where: 'agentic-patterns page · langgraph / plan_execute / crewai agents', src: 'Portals/admin-portal/src/app/features/resources/agentic-patterns.component.ts', next: '6/10 built — add <b>Reflection, Evaluator-optimizer, ReWOO, ToT</b>' },
    { area: 'Frameworks', domain: 'Frameworks / SDKs / runtimes (8)', status: 'built', where: 'explore (langgraph/crewai/llamaindex/haystack) + agentic-service (openai-agents/google-adk/msagent/strands)', src: 'Middleware/agentic-service/app/frameworks', next: '—' },
    { area: 'Inference', domain: 'LLMs &amp; multi-provider inference', status: 'built', where: '<code>providers.py</code> fan-out (OpenAI/Groq/Gemini/Anthropic/Bedrock/HF)', src: 'Middleware/vehicle-explore-service/app/providers.py', next: '—' },
    { area: 'Inference', domain: 'Local inference runtimes', status: 'planned', where: '—', src: null, next: 'add <b>vLLM / Ollama / TGI</b> as providers' },
    { area: 'Routing', domain: 'Framework + compound (auto) routers', status: 'built', where: '<code>frameworks.py</code> (URL router + <code>auto</code>)', src: 'Middleware/vehicle-explore-service/app/frameworks.py#L34', next: '—' },
    { area: 'Routing', domain: 'Semantic &amp; cost routers', status: 'partial', where: 'heuristic only (<code>_is_compound</code>)', src: 'Middleware/vehicle-explore-service/app/frameworks.py#L34', next: 'embedding-based + cost/latency-aware routing' },
    { area: 'Retrieval', domain: 'Vector / FTS / hybrid retrieval', status: 'built', where: '<code>search.py</code>', src: 'Middleware/vehicle-explore-service/app/search.py', next: '—' },
    { area: 'Retrieval', domain: 'Advanced RAG', status: 'planned', where: '—', src: null, next: '<b>reranking → HyDE/expansion → GraphRAG</b>' },
    { area: 'RAG', domain: 'RAG pipeline', status: 'built', where: '<code>langgraph_agent.py</code> StateGraph', src: 'Middleware/vehicle-explore-service/app/langgraph_agent.py#L51', next: '—' },
    { area: 'Knowledge bases', domain: 'Vector stores (pgVector + Mongo Atlas)', status: 'built', where: '<code>search.py</code> / <code>mongo_search.py</code> / vector-config-service', src: 'Middleware/vector-config-service', next: '—' },
    { area: 'Context Eng.', domain: 'Context Engineering (CEF)', status: 'built', where: '<code>context-engine-service</code> (retrieval+memory+permission → assembly → reasoning → evolution)', src: 'ContextEnggFramework/Middleware/context-engine-service', next: 'deepen assembly strategies' },
    { area: 'Memory', domain: 'Memory management', status: 'partial', where: 'CEF chat memory + guardrails query ledgers', src: 'ContextEnggFramework/Middleware/context-engine-service', next: 'episodic/semantic/procedural + vector memory + eviction' },
    { area: 'Tools', domain: 'Tools &amp; sandboxes', status: 'partial', where: '<code>tools.py</code> (<code>fetch_page</code>)', src: 'Middleware/vehicle-explore-service/app/tools.py', next: 'a sandboxed code/tool-execution tool' },
    { area: 'Protocols', domain: 'MCP (Model Context Protocol)', status: 'planned', where: '—', src: null, next: 'expose VKP tools/KB as an MCP server + consume MCP in agents' },
    { area: 'Protocols', domain: 'A2A (Agent-to-Agent)', status: 'planned', where: '—', src: null, next: 'agent-to-agent protocol between explore/agentic/CEF' },
    { area: 'Protocols', domain: 'OpenAPI / Swagger', status: 'built', where: 'springdoc (Java) + FastAPI <code>/docs</code>', src: null, next: '—' },
    { area: 'Auth', domain: 'AuthN/Z (JWT-RBAC + session)', status: 'partial', where: '<code>vkp-jwt-rbac</code> + <code>vkp-session-security</code>', src: 'Middleware/vkp-jwt-rbac', next: 'real <b>OAuth2 / OIDC</b> flow' },
    { area: 'Safety', domain: 'Guardrails / safety', status: 'built', where: '<code>guardrails-service</code> (LLM Guard / Groq safeguard)', src: 'Middleware/guardrails-service', next: '—' },
    { area: 'Eval', domain: 'Eval / harness', status: 'planned', where: '—', src: null, next: '<b>LLM-as-judge</b> + trajectory scoring to compare frameworks' },
    { area: 'Orchestration', domain: 'Airflow DAGs', status: 'built', where: '<code>Workflows/AirflowDAGS</code>', src: 'Middleware/Workflows/AirflowDAGS', next: '—' },
    { area: 'Observability', domain: 'OTel / Prometheus / Grafana', status: 'partial', where: '<code>DevOps/Localhost/Observability</code>', src: 'DevOps/Localhost/Observability', next: 're-enable + dashboards' },
    { area: 'Infra', domain: 'Docker / k8s / Terraform / AWS CFN', status: 'built', where: '<code>Infra/</code> + <code>DevOps/</code>', src: 'Infra', next: '—' },
  ];

  readonly roadmap = [
    { name: '1 · Finish the agentic patterns', state: 'next', why: 'Reflection → Evaluator-optimizer → ReWOO → ToT as roster search frameworks. Small, self-contained, closes the catalog; gives a reusable judge for step 2.' },
    { name: '2 · Eval / harness', state: 'planned', why: 'LLM-as-judge + trajectory scoring so every later cycle is measurable against the others.' },
    { name: '3 · Advanced RAG', state: 'planned', why: 'reranking → HyDE/expansion → GraphRAG — the biggest answer-quality win, scorable with step 2.' },
    { name: '4 · Memory management', state: 'planned', why: 'episodic/semantic/procedural + vector memory on CEF — prerequisite for serious multi-turn agents.' },
    { name: '5 · MCP', state: 'planned', why: 'expose VKP tools/KB as an MCP server + consume MCP in agents — high-leverage protocol.' },
    { name: '6 · Tools &amp; sandboxes', state: 'planned', why: 'sandboxed code/tool execution — complements MCP.' },
    { name: '7 · A2A', state: 'planned', why: 'agent-to-agent protocol between services — rides on MCP/tools maturity.' },
    { name: '8 · Local inference', state: 'planned', why: 'vLLM / Ollama / TGI as providers — infra-ish, independent.' },
    { name: '9 · Semantic &amp; cost routers', state: 'planned', why: 'embedding + cost/latency-aware model routing — benefits from steps 2 &amp; 8.' },
    { name: '10 · OAuth2 / OIDC', state: 'planned', why: 'real auth flows alongside the custom JWT — orthogonal, safely last.' },
  ];
}
