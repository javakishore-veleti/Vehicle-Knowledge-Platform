import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Design Patterns → Agentic Patterns. Reference page: ReAct + the alternative
 *  agent/orchestration patterns, and how they map onto VKP's stages. */
@Component({
  selector: 'app-agentic-patterns',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page ap">
    <h2>Agentic Patterns</h2>
    <p class="lead">
      <b>ReAct is an agent design pattern</b>, not a framework feature. Note on the name: it's
      <b>ReAct = <u>Rea</u>soning + <u>Act</u>ing</b> (Yao et al., 2022) — <i>not</i> React.js.
      LangGraph's <code>create_react_agent</code> is just a prebuilt implementation of that pattern.
    </p>

    <nav class="toc">
      <div class="toc-title">Contents</div>
      <ol>
        <li><a (click)="go('s-react')">What ReAct is</a></li>
        <li><a (click)="go('s-plan')">What Plan-and-Execute is</a></li>
        <li><a (click)="go('s-patterns')">The main agent / orchestration patterns</a></li>
        <li><a (click)="go('s-usecases')">VKP use cases per pattern (5 each)</a></li>
        <li><a (click)="go('s-vkp')">How this maps to VKP</a></li>
        <li><a (click)="go('s-impl')">What is plan-execute built on?</a></li>
        <li><a (click)="go('s-ref')">Reference implementations — Plan-and-Execute on 7 frameworks</a></li>
      </ol>
    </nav>

    <h3 id="s-react">What ReAct is</h3>
    <p>The LLM runs a loop, interleaving <b>Thought → Action (tool call) → Observation</b>, until it has
       enough to answer:</p>
    <pre class="flow">Thought: I need the page's links  →  Action: fetch_page(seed)  →  Observation: {{ '{' }}links:[…]{{ '}' }}
Thought: these are the vehicle pages  →  Final answer: [JSON links]</pre>
    <p>That's exactly the <b>collect</b> stage in this codebase.</p>

    <h3 id="s-plan">What Plan-and-Execute is</h3>
    <p>Instead of deciding one tool at a time (ReAct), the model first writes a <b>plan</b> — the whole
       list of steps — then an executor runs each step, <b>optionally re-planning</b> when a step fails or
       new information appears:</p>
    <pre class="flow">Plan:       1. towing capacity of the Tacoma   2. hybrid options for the Ranger   3. 2026 price of the Canyon
Execute:    retrieve each sub-query  →  (re-plan if a step returns nothing)
Synthesize: one cited comparison over the merged results</pre>
    <p>That's exactly the <b>search · plan-execute</b> framework here — best for compound questions a single
       retrieval can't cover. See <a class="ilink" (click)="go('s-impl')">what it's built on</a> below.</p>

    <h3 id="s-patterns">The main agent / orchestration patterns</h3>
    <table class="ap-table">
      <thead><tr><th>Pattern</th><th>Idea</th><th>One-liner</th><th>In VKP</th></tr></thead>
      <tbody>
        <tr *ngFor="let p of patterns" [class.react]="p.done">
          <td><b>{{ p.pattern }}</b></td><td>{{ p.idea }}</td><td>{{ p.oneliner }}</td>
          <td><span [innerHTML]="p.vkp"></span><a *ngIf="p.src" class="src" [href]="repo + '/' + p.src"
              target="_blank" rel="noopener" [title]="'Source: ' + p.src">&nbsp;↗</a></td>
        </tr>
      </tbody>
    </table>

    <p class="frame">
      A useful framing (Anthropic's <i>Building Effective Agents</i>): <b>workflows</b> are deterministic
      graphs you design (prompt chaining, routing, parallelization, orchestrator-workers,
      evaluator-optimizer), while <b>agents</b> are autonomous loops where the model drives control
      flow — ReAct being the canonical agent loop.
    </p>

    <h3 id="s-usecases">VKP use cases per pattern <span class="dim">(pick one to implement next)</span></h3>
    <p>Five project-specific use cases for each pattern — the <span class="badge">built</span> tag marks
       what's already implemented; the rest are candidates we can build one at a time.</p>
    <div class="uc" *ngFor="let u of useCases">
      <div class="uc-h"><b>{{ u.pattern }}</b></div>
      <ol>
        <li *ngFor="let c of u.cases"><span [innerHTML]="c.t"></span>
          <span *ngIf="c.done" class="badge">built</span></li>
      </ol>
    </div>

    <h3 id="s-vkp">How this maps to VKP</h3>
    <ul class="map">
      <li *ngFor="let m of mapping"><b>{{ m.k }}</b> → <span [innerHTML]="m.v"></span></li>
    </ul>
    <p class="foot">On the <a routerLink="/agents/roster">Agent Roster</a>, picking a different
       <b>framework</b> for a stage is effectively picking a different <b>agent implementation</b>
       (and sometimes a different pattern) behind the same endpoint.</p>

    <h3 id="s-impl">What is plan-execute built on? <span class="dim">(no framework)</span></h3>
    <p>VKP's live <code>plan-execute</code> search framework is <b>plain, hand-rolled Python</b> — it does
       <b>not</b> sit on LangGraph, CrewAI, LlamaIndex, Haystack, or any agent SDK. The only SDK touched is
       the <b>OpenAI client</b> (for the planning call + answer generation) — an LLM client, not an agent
       framework.</p>
    <table class="ap-table">
      <thead><tr><th>Phase</th><th>Implementation</th><th>Framework?</th></tr></thead>
      <tbody>
        <tr><td><b>Plan</b></td><td><code>providers.complete()</code> — a raw chat-completion call</td><td>OpenAI client only</td></tr>
        <tr><td><b>Execute</b></td><td>a plain loop over <code>frameworks._retrieve()</code> → <code>search.search_chunks()</code></td><td>Python + psycopg2 / pgvector</td></tr>
        <tr><td><b>Merge</b></td><td><code>_merge()</code> — dedup by source+snippet, best score first</td><td>pure Python</td></tr>
        <tr><td><b>Synthesize</b></td><td><code>frameworks.synthesize()</code> → <code>providers.generate_all()</code></td><td>OpenAI / Bedrock clients</td></tr>
      </tbody>
    </table>
    <p>Kept dependency-free because <i>plan → loop-retrieve → synthesize</i> is simple enough that a graph
       or crew framework would be overhead. The <code>auto</code> router (compound → plan-execute, simple →
       langgraph) is likewise a plain regex / brand-set heuristic — no SDK.</p>

    <h3 id="s-ref">Reference implementations — Plan-and-Execute on 7 frameworks</h3>
    <p>For comparison, the repo also ships idiomatic Plan-and-Execute reference implementations of the same
       pattern on each major framework, under
       <code>Middleware/Reference/plan_and_execute/</code> (reference/educational — each needs its SDK + an
       LLM key to run; not wired into the live services):</p>
    <table class="ap-table">
      <thead><tr><th>Framework</th><th>How it expresses Plan-and-Execute</th><th>File</th></tr></thead>
      <tbody>
        <tr *ngFor="let r of refs">
          <td><b>{{ r.fw }}</b></td><td [innerHTML]="r.how"></td>
          <td><a [href]="repo + '/Middleware/Reference/plan_and_execute/' + r.file" target="_blank" rel="noopener"><code>{{ r.file }}</code></a></td>
        </tr>
      </tbody>
    </table>
    <p class="foot">The shipping version that actually runs is the framework-free
       <code>plan_execute_agent.py</code> + the <code>auto</code> router — these references are the
       "how would I do it on X?" companions.</p>
  </div>
  `,
  styles: [`
    .ap { padding: 1rem 1.5rem; max-width: 1040px; }
    .ap h2 { margin: 0 0 .4rem; }
    .ap h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .ap .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .ap code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.93rem; }
    .ap .flow { background:#0c111d; color:#d1e0ff; padding:.8rem; border-radius:8px; font-size:.82rem; white-space:pre-wrap; line-height:1.6; }
    .ap-table { border-collapse:collapse; width:100%; font-size:.98rem; margin:.5rem 0 1rem; }
    .ap-table th, .ap-table td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; vertical-align:top; }
    .ap-table thead th { background:#f6f1ff; color:#4c1d95; }
    .ap-table tbody tr:hover { background:#faf8ff; }
    .ap-table tr.react { background:#f3eefe; }
    .ap-table tr.react:hover { background:#ede7ff; }
    .ap .frame { background:#f7f9ff; border:1px solid #e0e7ff; border-left:3px solid #3538cd; border-radius:6px; padding:.7rem .9rem; font-size:.98rem; line-height:1.6; color:#344054; }
    .ap .map { line-height:1.7; color:#344054; font-size:1.02rem; }
    .ap .map code { font-size:.82rem; }
    .ap .foot { color:#475467; font-size:.98rem; }
    .ap .foot a { color:#3538cd; }
    .ap .dim { color:#94a3b8; font-weight:400; font-size:.9rem; }
    .toc { background:#faf8ff; border:1px solid #e9e3fb; border-left:3px solid #7c3aed; border-radius:8px;
      padding:.7rem 1rem .8rem; margin:1rem 0 1.5rem; max-width:560px; }
    .toc-title { font-size:.74rem; letter-spacing:.08em; text-transform:uppercase; font-weight:700;
      color:#7b74a8; margin-bottom:.45rem; }
    .toc ol { margin:0; padding-left:1.4rem; }
    .toc li { margin:.28rem 0; font-size:.96rem; }
    .toc li::marker { color:#a855f7; font-weight:700; }
    .toc a { color:#3538cd; cursor:pointer; text-decoration:none; }
    .toc a:hover { text-decoration:underline; }
    .ap .ilink { color:#3538cd; cursor:pointer; text-decoration:underline; }
    .ap-table a.src { color:#7c3aed; text-decoration:none; font-weight:700; }
    .ap-table a.src:hover { text-decoration:underline; }
    .ap-table a code { color:#3538cd; }
    .uc { margin:.4rem 0 .9rem; }
    .uc-h { font-weight:700; color:#4c1d95; margin:.6rem 0 .15rem; font-size:1rem; }
    .uc ol { margin:.15rem 0; padding-left:1.35rem; }
    .uc li { margin:.22rem 0; color:#344054; font-size:.95rem; line-height:1.5; }
    .uc li::marker { color:#a855f7; }
    .badge { background:#ecfdf3; color:#0f8a5f; border:1px solid #b7f0d2; border-radius:10px;
      padding:0 .45rem; font-size:.72rem; font-weight:700; margin-left:.4rem; vertical-align:middle; white-space:nowrap; }
  `]
})
export class AgenticPatternsComponent {
  readonly repo = 'https://github.com/javakishore-veleti/Vehicle-Knowledge-Platform/blob/main';

  go(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  readonly refs = [
    { fw: 'LangGraph', how: 'a compiled <code>StateGraph</code>: plan → execute → synthesize nodes', file: 'langgraph_pe.py' },
    { fw: 'CrewAI', how: 'a planner Agent + Task emits sub-queries; synthesizer follows', file: 'crewai_pe.py' },
    { fw: 'LlamaIndex', how: 'the built-in <code>SubQuestionQueryEngine</code> (native plan-and-execute) + manual variant', file: 'llamaindex_pe.py' },
    { fw: 'Haystack 2.x', how: 'a <code>PromptBuilder → Generator</code> planner pipeline, then fan-out', file: 'haystack_pe.py' },
    { fw: 'OpenAI Agents SDK', how: 'a planner <code>Agent</code> via <code>Runner.run_sync</code>', file: 'openai_pe.py' },
    { fw: 'Google ADK', how: 'a planner <code>LlmAgent</code> driven by the async <code>InMemoryRunner</code>', file: 'google_pe.py' },
    { fw: 'Microsoft Agent Framework', how: 'an <code>OpenAIChatClient</code> planner agent', file: 'msagent_pe.py' },
  ];

  readonly useCases = [
    { pattern: 'ReAct', cases: [
      { t: '<b>Smart link discovery</b> — a scout crawls a seed and decides which links to follow from what it finds (the <code>collect</code> stage).', done: true },
      { t: '<b>Single-model deep-dive</b> — given "2026 RAV4", iteratively fetch the spec → trims → pricing pages as it discovers links.' },
      { t: '<b>Recall / safety lookup</b> — navigate manufacturer / NHTSA pages to find the specific recall for a model-year.' },
      { t: '<b>Dealer / inventory locator</b> — step through a dealer site\'s search to find local stock for a model + ZIP.' },
      { t: '<b>Broken-link repair</b> — when a stored resource 404s, search the site to find the moved page and update the graph.' },
    ]},
    { pattern: 'Plan-and-Execute', cases: [
      { t: '<b>Multi-brand comparison search</b> — towing / hybrid / price across Toyota vs Ford vs GMC (the <code>plan-execute</code> framework).', done: true },
      { t: '<b>Buyer\'s-guide builder</b> — plan: list candidates → fetch specs → fetch price → fetch safety → rank.' },
      { t: '<b>Adaptive company onboarding</b> — plan the discover → ingest → index steps per site, re-planning for JS-heavy sites.' },
      { t: '<b>Spec-sheet assembly</b> — one retrieval per spec dimension, composed into a side-by-side table for N models.' },
      { t: '<b>Total-cost-of-ownership report</b> — sub-queries for price, MPG, maintenance, insurance and resale per model.' },
    ]},
    { pattern: 'ReWOO', cases: [
      { t: '<b>Batch spec enrichment</b> — plan all fetch calls for a known model list up front, run them in parallel, no per-step LLM.' },
      { t: '<b>Parallel multi-brand facts</b> — gather the same N facts for M brands in one planned batch.' },
      { t: '<b>Nightly price refresh</b> — plan every price-fetch for tracked models upfront, execute LLM-free.' },
      { t: '<b>Bulk image alt-text</b> — plan captions for every image in a snapshot in one shot.' },
      { t: '<b>Fixed-dimension comparison</b> — when the facets are fixed (towing/mpg/price/seats), plan all retrievals upfront (no need to observe between).' },
    ]},
    { pattern: 'Reflection / Reflexion', cases: [
      { t: '<b>Answer quality gate</b> — draft an answer, a critic checks it\'s grounded + on-topic, revise if not (cuts hallucination).' },
      { t: '<b>Chunk quality review</b> — after chunking, critique chunks for coherence/self-containment, re-chunk the bad ones.' },
      { t: '<b>Citation verification</b> — check every claim maps to a cited source; drop or fix the unsupported ones.' },
      { t: '<b>Crawl coverage self-check</b> — "did I miss the EV / trucks section?" → trigger a targeted re-crawl.' },
      { t: '<b>Spec-extraction accuracy</b> — verify extracted specs against the raw page (does towing = 5,000 lb appear?), correct mismatches.' },
    ]},
    { pattern: 'Tree of Thoughts (ToT)', cases: [
      { t: '<b>"Best car for me"</b> — branch on priority weightings (budget-first / space-first / efficiency-first), score each, pick the best.' },
      { t: '<b>Ambiguous-query disambiguation</b> — "fast Toyota" → branch GR Corolla / Supra / Tacoma TRD, evaluate, choose.' },
      { t: '<b>Trim / option optimizer</b> — explore trim+option combos to hit a budget/feature target, backtrack on dead ends.' },
      { t: '<b>Multi-constraint filter</b> — AWD + 3-row + under $45k + hybrid: search the constraint tree for a vehicle that fits.' },
      { t: '<b>Spec-conflict resolver</b> — two sources disagree on a spec → branch hypotheses (year / trim / market), resolve.' },
    ]},
    { pattern: 'Router / dispatcher', cases: [
      { t: '<b>Compound-vs-simple routing</b> — the <code>auto</code> framework sends compound queries to plan-execute, simple ones to langgraph.', done: true },
      { t: '<b>Framework router</b> — the framework name in the URL routes to langgraph / crewai / llamaindex / haystack.', done: true },
      { t: '<b>Query-type router</b> — spec → vector search, "where to buy" → dealer tool, recall → safety source, price → pricing index.' },
      { t: '<b>Store router</b> — route a query to pgVector / MongoDB / a specific company\'s index based on the question.' },
      { t: '<b>Topic / guardrail router</b> — off-topic → polite refusal, vehicle → pipeline, unsafe → block.' },
    ]},
    { pattern: 'RAG pipeline', cases: [
      { t: '<b>Single-fact vehicle Q&amp;A</b> — "what\'s the Camry\'s MPG?" (the <code>langgraph</code> search graph).', done: true },
      { t: '<b>Company-scoped FAQ</b> — answers restricted to one brand\'s indexed content.' },
      { t: '<b>Brochure / PDF lookup</b> — retrieve from ingested brochures and answer with citations.' },
      { t: '<b>"Explain this feature"</b> — retrieve feature descriptions across models and summarize.' },
      { t: '<b>Snapshot-grounded answer</b> — answer strictly from a specific crawl snapshot\'s content.' },
    ]},
    { pattern: 'Multi-agent (supervisor / workers)', cases: [
      { t: '<b>Researcher + advisor crew</b> — a researcher gathers sources, an advisor writes the answer (the <code>crewai</code> search).', done: true },
      { t: '<b>Per-brand workers</b> — a supervisor dispatches one worker per brand for a comparison, then merges.' },
      { t: '<b>Onboarding crew</b> — separate crawler / extractor / indexer agents coordinated for one company.' },
      { t: '<b>Review aggregator</b> — workers pull reviews from different sources, supervisor synthesizes a consensus.' },
      { t: '<b>Spec / price / safety specialists</b> — three specialist agents, a supervisor composes the buyer\'s report.' },
    ]},
    { pattern: 'Evaluator-optimizer', cases: [
      { t: '<b>Answer refiner</b> — generate → judge completeness + citations → regenerate until it passes.' },
      { t: '<b>Chunking optimizer</b> — try chunk sizes/overlaps, judge retrieval on sample queries, keep the best.' },
      { t: '<b>Query rewriter</b> — rewrite the search query until retrieval is relevant (boosts recall).' },
      { t: '<b>Summary tightener</b> — optimize a spec summary for accuracy + length against the source.' },
      { t: '<b>Embedding-model selector</b> — score candidate embedding models on a labeled query set, pick the winner.' },
    ]},
    { pattern: 'Prompt chaining / parallelization', cases: [
      { t: '<b>Multi-provider answer fan-out</b> — ask N LLMs the same question and compare (<code>providers.generate_all</code>).', done: true },
      { t: '<b>Ingestion chain</b> — fetch → clean → extract title → hash → store (the ingestion DAG).', done: true },
      { t: '<b>Sectioning</b> — split a long brochure into sections, summarize each in parallel, merge.' },
      { t: '<b>Voting</b> — N models answer one spec question, take the majority (anti-hallucination).' },
      { t: '<b>Translate-then-index</b> — translate non-English content → chunk → embed (multilingual support).' },
    ]},
  ];

  readonly patterns = [
    { pattern: 'ReAct', idea: 'reason ↔ act loop', oneliner: 'dynamically decide the next tool from observations (what collect uses)', done: true, vkp: '✅ collect · <code>langgraph</code>', src: 'Middleware/vehicle-explore-service/app/langgraph_agent.py#L89' },
    { pattern: 'Plan-and-Execute', idea: 'plan first, then do', oneliner: 'generate a full multi-step plan up front, execute each step, optionally re-plan', done: true, vkp: '✅ search · <code>plan-execute</code>', src: 'Middleware/vehicle-explore-service/app/plan_execute_agent.py#L64' },
    { pattern: 'ReWOO', idea: 'plan tools without observations', oneliner: 'decide all tool calls in one shot to save tokens/latency, then run them', done: false, vkp: '—', src: null },
    { pattern: 'Reflection / Reflexion', idea: 'self-critique', oneliner: 'produce output → critique it → revise; iterate to improve quality', done: false, vkp: '—', src: null },
    { pattern: 'Tree of Thoughts (ToT)', idea: 'search over reasoning', oneliner: 'branch into multiple reasoning paths, score, backtrack — for hard problems', done: false, vkp: '—', src: null },
    { pattern: 'Router / dispatcher', idea: 'classify then route', oneliner: 'pick the right tool/chain/sub-agent for the input (no loop needed)', done: true, vkp: '✅ <code>auto</code> router + <code>frameworks.run</code>', src: 'Middleware/vehicle-explore-service/app/frameworks.py#L34' },
    { pattern: 'RAG pipeline', idea: 'retrieve → generate', oneliner: 'fixed graph: fetch context, then answer (no autonomous tool loop)', done: true, vkp: '✅ search · <code>langgraph</code> StateGraph', src: 'Middleware/vehicle-explore-service/app/langgraph_agent.py#L51' },
    { pattern: 'Multi-agent (supervisor / orchestrator-workers)', idea: 'delegate', oneliner: 'a supervisor splits work to specialized sub-agents that collaborate', done: true, vkp: '~ <code>crewai</code> sequential crews', src: 'Middleware/vehicle-explore-service/app/crewai_agent.py#L35' },
    { pattern: 'Evaluator-optimizer', idea: 'generate ↔ judge', oneliner: 'one model produces, another grades/refines in a loop', done: false, vkp: '—', src: null },
    { pattern: 'Prompt chaining / parallelization', idea: 'workflows', oneliner: 'deterministic step pipelines, or fan-out-then-merge (voting/sectioning)', done: true, vkp: '✅ crewai chains · multi-provider fan-out', src: 'Middleware/vehicle-explore-service/app/providers.py#L193' },
  ];

  readonly mapping = [
    { k: 'collect stage', v: '<b>ReAct</b> (<code>create_react_agent</code>, decides to call <code>fetch_page</code>) — <code>langgraph_agent.py</code>' },
    { k: 'search stage', v: 'a <b>RAG pipeline</b> (a fixed <code>StateGraph</code>: retrieve → generate), <i>not</i> ReAct — same file' },
    { k: 'search · plan-execute', v: '<b>Plan-and-Execute</b> — a planner LLM splits a compound query into sub-queries, retrieves each, then synthesizes a cited comparison — <code>plan_execute_agent.py</code>' },
    { k: 'search · auto', v: '<b>Router</b> — the <code>auto</code> framework sends compound/comparison queries to plan-execute, simple ones to langgraph (cheap heuristic, no LLM)' },
    { k: 'index stage', v: 'a <b>single structured LLM call</b> (no tools, no loop) — <code>_chunk()</code> just prompts the model to return chunk JSON' },
    { k: 'multi-provider answers (providers.py)', v: 'a <b>parallelization / voting</b>-style fan-out (ask N providers, compare)' },
    { k: 'agentic-service roster', v: 'different SDKs (openai-agents, google-adk, msagent, strands…) that each implement these patterns their own way — the point of the pluggable roster: swap the agent pattern/SDK behind the same collect/index/search API' },
  ];
}
