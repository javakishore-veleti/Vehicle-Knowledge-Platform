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

    <h3>VKP use cases per pattern <span class="dim">(✓ = runnable in {{ fw.name }} now · ○ = planned)</span></h3>
    <p class="hint">The 5 concrete use cases per pattern. Run one: <code>POST /agent-patterns/&lt;pattern&gt;/{{ fwKey }}/run</code>
       with <code>{{ '{' }}"input":"…","useCase":"&lt;id&gt;"{{ '}' }}</code>.</p>
    <div class="ucp" *ngFor="let p of fw.rows">
      <div class="ucp-h"><b>{{ p.name }}</b></div>
      <div class="ucs">
        <span class="uc" *ngFor="let u of ucs(p.key)" [class.done]="u.done">
          <span class="b">{{ u.done ? '✓' : '○' }}</span> {{ u.name }} <code>{{ u.id }}</code>
        </span>
      </div>
    </div>

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
    .ucp { margin:.3rem 0 .6rem; }
    .ucp-h { font-weight:700; color:#4c1d95; margin:.55rem 0 .2rem; }
    .ucs { display:flex; flex-wrap:wrap; gap:.4rem; }
    .uc { font-size:.85rem; color:#64748b; background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:.1rem .6rem; }
    .uc.done { color:#0f8a5f; background:#ecfdf3; border-color:#b7f0d2; }
    .uc .b { font-weight:800; }
    .uc code { font-size:.74rem; background:transparent; }
    .hint { color:#475467; font-size:.9rem; margin:.2rem 0 .7rem; }
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

  ucs(patternKey: string): { id: string; name: string; done: boolean }[] {
    const impl = IMPL[this.fwKey] || new Set<string>();
    return (USECASES[patternKey] || []).map(u => ({ ...u, done: impl.has(patternKey + ':' + u.id) }));
  }
}

const USECASES: Record<string, { id: string; name: string }[]> = {
  reflection: [{ id: 'answer-quality-gate', name: 'Answer quality gate' }, { id: 'chunk-quality-review', name: 'Chunk quality review' }, { id: 'citation-verification', name: 'Citation verification' }, { id: 'crawl-coverage-self-check', name: 'Crawl coverage self-check' }, { id: 'spec-extraction-accuracy', name: 'Spec-extraction accuracy' }],
  react: [{ id: 'smart-link-discovery', name: 'Smart link discovery' }, { id: 'single-model-deep-dive', name: 'Single-model deep-dive' }, { id: 'recall-safety-lookup', name: 'Recall / safety lookup' }, { id: 'dealer-inventory-locator', name: 'Dealer / inventory locator' }, { id: 'broken-link-repair', name: 'Broken-link repair' }],
  'plan-execute': [{ id: 'multi-brand-comparison', name: 'Multi-brand comparison' }, { id: 'buyers-guide-builder', name: "Buyer's-guide builder" }, { id: 'adaptive-onboarding', name: 'Adaptive onboarding' }, { id: 'spec-sheet-assembly', name: 'Spec-sheet assembly' }, { id: 'tco-report', name: 'TCO report' }],
  rag: [{ id: 'single-fact-qa', name: 'Single-fact Q&A' }, { id: 'company-scoped-faq', name: 'Company-scoped FAQ' }, { id: 'brochure-pdf-lookup', name: 'Brochure / PDF lookup' }, { id: 'explain-feature', name: 'Explain this feature' }, { id: 'snapshot-grounded', name: 'Snapshot-grounded' }],
  router: [{ id: 'compound-vs-simple', name: 'Compound-vs-simple' }, { id: 'framework-router', name: 'Framework router' }, { id: 'query-type-router', name: 'Query-type router' }, { id: 'store-router', name: 'Store router' }, { id: 'topic-guardrail-router', name: 'Topic / guardrail router' }],
  chaining: [{ id: 'multi-provider-fanout', name: 'Multi-provider fan-out' }, { id: 'ingestion-chain', name: 'Ingestion chain' }, { id: 'sectioning', name: 'Sectioning' }, { id: 'voting', name: 'Voting' }, { id: 'translate-then-index', name: 'Translate-then-index' }],
  'multi-agent': [{ id: 'researcher-advisor', name: 'Researcher + advisor' }, { id: 'per-brand-workers', name: 'Per-brand workers' }, { id: 'onboarding-crew', name: 'Onboarding crew' }, { id: 'review-aggregator', name: 'Review aggregator' }, { id: 'spec-price-safety', name: 'Spec/price/safety specialists' }],
  'evaluator-optimizer': [{ id: 'answer-refiner', name: 'Answer refiner' }, { id: 'chunking-optimizer', name: 'Chunking optimizer' }, { id: 'query-rewriter', name: 'Query rewriter' }, { id: 'summary-tightener', name: 'Summary tightener' }, { id: 'embedding-model-selector', name: 'Embedding-model selector' }],
  rewoo: [{ id: 'batch-spec-enrichment', name: 'Batch spec enrichment' }, { id: 'parallel-multi-brand-facts', name: 'Parallel multi-brand facts' }, { id: 'nightly-price-refresh', name: 'Nightly price refresh' }, { id: 'bulk-image-alt-text', name: 'Bulk image alt-text' }, { id: 'fixed-dimension-comparison', name: 'Fixed-dimension comparison' }],
  tot: [{ id: 'best-car-for-me', name: '"Best car for me"' }, { id: 'ambiguous-query', name: 'Ambiguous-query' }, { id: 'trim-optimizer', name: 'Trim / option optimizer' }, { id: 'multi-constraint-filter', name: 'Multi-constraint filter' }, { id: 'spec-conflict-resolver', name: 'Spec-conflict resolver' }],
};

const IMPL: Record<string, Set<string>> = {
  langgraph: new Set(['reflection:answer-quality-gate', 'reflection:chunk-quality-review', 'reflection:citation-verification', 'reflection:crawl-coverage-self-check', 'reflection:spec-extraction-accuracy',
    'rag:single-fact-qa', 'rag:company-scoped-faq', 'rag:brochure-pdf-lookup', 'rag:explain-feature', 'rag:snapshot-grounded',
    'evaluator-optimizer:answer-refiner', 'evaluator-optimizer:chunking-optimizer', 'evaluator-optimizer:query-rewriter', 'evaluator-optimizer:summary-tightener', 'evaluator-optimizer:embedding-model-selector',
    'router:compound-vs-simple', 'router:framework-router', 'router:query-type-router', 'router:store-router', 'router:topic-guardrail-router',
    'plan-execute:multi-brand-comparison', 'plan-execute:buyers-guide-builder', 'plan-execute:adaptive-onboarding', 'plan-execute:spec-sheet-assembly', 'plan-execute:tco-report',
    'multi-agent:researcher-advisor', 'multi-agent:per-brand-workers', 'multi-agent:onboarding-crew', 'multi-agent:review-aggregator', 'multi-agent:spec-price-safety',
    'rewoo:batch-spec-enrichment', 'rewoo:parallel-multi-brand-facts', 'rewoo:nightly-price-refresh', 'rewoo:bulk-image-alt-text', 'rewoo:fixed-dimension-comparison',
    'tot:best-car-for-me', 'tot:ambiguous-query', 'tot:trim-optimizer', 'tot:multi-constraint-filter', 'tot:spec-conflict-resolver',
    'chaining:multi-provider-fanout', 'chaining:ingestion-chain', 'chaining:sectioning', 'chaining:voting', 'chaining:translate-then-index',
    'react:smart-link-discovery', 'react:single-model-deep-dive', 'react:recall-safety-lookup', 'react:dealer-inventory-locator', 'react:broken-link-repair']),
  crewai: new Set(['reflection:answer-quality-gate', 'reflection:chunk-quality-review', 'reflection:citation-verification', 'reflection:crawl-coverage-self-check', 'reflection:spec-extraction-accuracy',
    'evaluator-optimizer:answer-refiner', 'evaluator-optimizer:chunking-optimizer', 'evaluator-optimizer:query-rewriter', 'evaluator-optimizer:summary-tightener', 'evaluator-optimizer:embedding-model-selector',
    'chaining:multi-provider-fanout', 'chaining:ingestion-chain', 'chaining:sectioning', 'chaining:voting', 'chaining:translate-then-index',
    'router:compound-vs-simple', 'router:framework-router', 'router:query-type-router', 'router:store-router', 'router:topic-guardrail-router',
    'tot:best-car-for-me', 'tot:ambiguous-query', 'tot:trim-optimizer', 'tot:multi-constraint-filter', 'tot:spec-conflict-resolver',
    'rewoo:batch-spec-enrichment', 'rewoo:parallel-multi-brand-facts', 'rewoo:nightly-price-refresh', 'rewoo:bulk-image-alt-text', 'rewoo:fixed-dimension-comparison',
    'multi-agent:researcher-advisor', 'multi-agent:per-brand-workers', 'multi-agent:onboarding-crew', 'multi-agent:review-aggregator', 'multi-agent:spec-price-safety',
    'plan-execute:multi-brand-comparison', 'plan-execute:buyers-guide-builder', 'plan-execute:adaptive-onboarding', 'plan-execute:spec-sheet-assembly', 'plan-execute:tco-report',
    'rag:single-fact-qa', 'rag:company-scoped-faq', 'rag:brochure-pdf-lookup', 'rag:explain-feature', 'rag:snapshot-grounded',
    'react:smart-link-discovery', 'react:single-model-deep-dive', 'react:recall-safety-lookup', 'react:dealer-inventory-locator', 'react:broken-link-repair']),
  llamaindex: new Set(['reflection:answer-quality-gate', 'reflection:chunk-quality-review', 'reflection:citation-verification', 'reflection:crawl-coverage-self-check', 'reflection:spec-extraction-accuracy',
    'tot:best-car-for-me', 'tot:ambiguous-query', 'tot:trim-optimizer', 'tot:multi-constraint-filter', 'tot:spec-conflict-resolver',
    'multi-agent:researcher-advisor', 'multi-agent:per-brand-workers', 'multi-agent:onboarding-crew', 'multi-agent:review-aggregator', 'multi-agent:spec-price-safety']),
};

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
  llamaindex: {
    name: 'LlamaIndex', file: 'llamaindex',
    blurb: 'The <b>LlamaIndex column</b> of <code>agent-patterns-service</code> (:8094): each pattern leans on a LlamaIndex-native construct where one exists — <code>VectorStoreIndex</code> for RAG, the 0.14 workflow <code>ReActAgent</code> for ReAct, and <code>SubQuestionQueryEngine</code> for plan-and-execute — the rest are LLM-orchestrated over <code>li.complete</code>. All 9 verified live.',
    rows: [
      { ...ROWS.react, idiom: 'native 0.14 workflow <code>ReActAgent</code> + <code>FunctionTool</code> (async run)', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'native <code>SubQuestionQueryEngine</code> (plan → sub-query → combine)', example: 'RAV4 Prime vs Camry decomposed for a commuter' },
      { ...ROWS.rag, idiom: 'native <code>VectorStoreIndex.as_query_engine</code> over the corpus', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'LLM classify → tailored handler (<code>li.complete</code>)', example: 'routed → recommend' },
      { ...ROWS.chain, idiom: '2-step LLM chain: rewrite → answer', example: 'RAV4 Prime 94 MPGe / 38 MPG' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety specialists → lead composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generate → judge → revise (one round)', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner emits blind tool calls → execute (no LLM) → solve', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'branch (propose 3) → evaluate (score) → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: '<code>li.complete</code> drives draft → critique → revise', example: 'refined RAV4 answer' },
    ],
  },
  haystack: {
    name: 'Haystack', file: 'haystack',
    blurb: 'The <b>Haystack column</b> of <code>agent-patterns-service</code> (:8094): Haystack 2.x shows best where its <b>Pipeline</b> graph and components fit — native <code>Agent</code>+<code>Tool</code> for ReAct, a BM25 <code>Pipeline</code> for RAG, and an <code>OutputAdapter</code>-wired chain — the rest orchestrate the <code>OpenAIGenerator</code>. All 9 verified live.',
    rows: [
      { ...ROWS.react, idiom: 'native <code>agents.Agent</code> + <code>tools.Tool</code> (chat-generator loop)', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'plan sub-questions → answer each → synthesize', example: 'RAV4 Prime vs Camry for a commuter' },
      { ...ROWS.rag, idiom: 'native <b>Pipeline</b>: BM25 retriever → PromptBuilder → generator', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'generator classifies → tailored prompt', example: 'routed → recommend' },
      { ...ROWS.chain, idiom: 'native <b>Pipeline</b>: rewrite → <code>OutputAdapter</code> → answer', example: 'RAV4 Prime 94 MPGe / 38 MPG' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety specialists → lead composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generate → judge → revise (one round)', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner (blind) → execute (no LLM) → solve', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'branch (propose 3) → evaluate (score) → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: 'generator drives draft → critique → revise', example: 'refined RAV4 answer' },
    ],
  },
  openai_agents: {
    name: 'OpenAI Agents SDK', file: 'openai_agents',
    blurb: 'The <b>OpenAI Agents SDK column</b> of <code>agent-patterns-service</code> (:8094): every pattern runs through the SDK\'s <code>Agent</code> + <code>Runner.run_sync</code> — ReAct and RAG use a real <code>@function_tool</code> agent loop, the rest compose multiple <code>Agent</code> runs. All 9 verified live on gpt-4o-mini.',
    rows: [
      { ...ROWS.react, idiom: 'native <code>Agent</code> + <code>@function_tool</code> + <code>Runner.run_sync</code>', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'planner Agent → execute sub-steps → synthesizer Agent', example: 'RAV4 Prime vs Camry for a commuter' },
      { ...ROWS.rag, idiom: 'Agent whose <code>@function_tool</code> retrieves from the corpus', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'classifier Agent → tailored specialist Agent', example: 'routed → recommend' },
      { ...ROWS.chain, idiom: '2-Agent chain: rewrite → answer (Runner)', example: 'RAV4 Prime 94 MPGe / 38 MPG' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety Agents → lead Agent composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generator Agent → judge Agent → revise (one round)', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner Agent (blind) → execute (no LLM) → solver Agent', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'proposer Agent (3) → judge Agent scores → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: 'writer + critic Agents, Runner.run_sync', example: 'refined RAV4 answer' },
    ],
  },
  google_adk: {
    name: 'Google ADK', file: 'google_adk',
    blurb: 'The <b>Google ADK column</b> of <code>agent-patterns-service</code> (:8094): every pattern is an ADK <code>LlmAgent</code> run through <code>InMemoryRunner</code> — ReAct and RAG use a native <code>FunctionTool</code> loop. ADK defaults to Gemini; here it is routed through <code>LiteLlm</code> → OpenAI (gpt-4o-mini). All 9 verified live.',
    rows: [
      { ...ROWS.react, idiom: 'native <code>LlmAgent</code> + <code>FunctionTool</code> (ADK tool loop)', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'planner LlmAgent → execute sub-steps → synthesizer LlmAgent', example: 'RAV4 Prime vs Camry for a commuter' },
      { ...ROWS.rag, idiom: 'LlmAgent whose <code>FunctionTool</code> retrieves from the corpus', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'classifier LlmAgent → tailored specialist LlmAgent', example: 'routed → recommend (CR-V)' },
      { ...ROWS.chain, idiom: '2-LlmAgent chain: rewrite → answer (InMemoryRunner)', example: 'RAV4 Prime 38 MPG combined' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety LlmAgents → lead LlmAgent composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generator LlmAgent → judge LlmAgent → revise', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner LlmAgent (blind) → execute (no LLM) → solver LlmAgent', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'proposer LlmAgent (3) → judge LlmAgent scores → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: 'writer + critic LlmAgents via InMemoryRunner', example: 'refined RAV4 answer' },
    ],
  },
  msagent: {
    name: 'Microsoft Agent Framework', file: 'msagent',
    blurb: 'The <b>Microsoft Agent Framework column</b> of <code>agent-patterns-service</code> (:8094): every pattern uses an <code>OpenAIChatClient.as_agent</code> Agent — ReAct and RAG with a native <code>@tool</code> loop. Each cell runs all its calls inside one event loop (AF\'s telemetry ContextVar breaks across repeated <code>asyncio.run</code>). All 9 verified live.',
    rows: [
      { ...ROWS.react, idiom: 'native <code>Agent</code> + <code>@tool</code> (AF tool loop)', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'planner Agent → execute sub-steps → synthesizer Agent', example: 'RAV4 Prime vs Camry for a commuter' },
      { ...ROWS.rag, idiom: 'Agent whose <code>@tool</code> retrieves from the corpus', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'classifier Agent → tailored specialist Agent', example: 'routed → recommend' },
      { ...ROWS.chain, idiom: '2-Agent chain: rewrite → answer (one event loop)', example: 'RAV4 Prime 94 MPGe' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety Agents → lead Agent composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generator Agent → judge Agent → revise', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner Agent (blind) → execute (no LLM) → solver Agent', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'proposer Agent (3) → judge Agent scores → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: 'writer + critic Agents (one event loop)', example: 'refined RAV4 answer' },
    ],
  },
  strands: {
    name: 'AWS Strands', file: 'strands',
    blurb: 'The <b>AWS Strands column</b> of <code>agent-patterns-service</code> (:8094): every pattern is a synchronous Strands <code>Agent</code> over <code>OpenAIModel</code> — ReAct and RAG with a native <code>@tool</code> loop. Strands is callable and sync (no asyncio), the simplest of the six SDKs. All 9 verified live.',
    rows: [
      { ...ROWS.react, idiom: 'native <code>Agent</code> + <code>@tool</code> (Strands agent loop)', example: 'tool-called → F-150 13,500 lb' },
      { ...ROWS.plan, idiom: 'planner Agent → execute sub-steps → synthesizer Agent', example: 'RAV4 Prime vs Camry for a commuter' },
      { ...ROWS.rag, idiom: 'Agent whose <code>@tool</code> retrieves from the corpus', example: '"RAV4 Prime range is 42 miles"' },
      { ...ROWS.router, idiom: 'classifier Agent → tailored specialist Agent', example: 'routed → recommend' },
      { ...ROWS.chain, idiom: '2-Agent chain: rewrite → answer (sync)', example: 'RAV4 Prime 38 MPG combined' },
      { ...ROWS.multi, idiom: 'spec/pricing/safety Agents → lead Agent composes', example: 'Model 3 buyer\'s report' },
      { ...ROWS.eval, idiom: 'generator Agent → judge Agent → revise', example: 'Highlander seating answer refined' },
      { ...ROWS.rewoo, idiom: 'planner Agent (blind) → execute (no LLM) → solver Agent', example: 'Tacoma base price $31,500' },
      { ...ROWS.tot, idiom: 'proposer Agent (3) → judge Agent scores → select', example: 'F-150 vs Tacoma towing → best pick' },
      { ...ROWS.reflect, idiom: 'writer + critic Agents (sync)', example: 'refined RAV4 answer' },
    ],
  },
};
