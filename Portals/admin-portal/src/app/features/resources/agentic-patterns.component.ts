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
       what's already implemented. Each pattern's table breaks every use case down into <b>that pattern's
       named phases</b> (e.g. ReAct → <b>Re</b>asoning / <b>Act</b>ing; ReWOO → <b>Re</b>asoning /
       <b>W</b>ith<b>O</b>ut <b>O</b>bservation).</p>
    <div class="uc" *ngFor="let u of useCases">
      <div class="uc-h"><b>{{ u.pattern }}</b></div>
      <table class="ap-table uc-table">
        <thead><tr><th>Use case</th><th *ngFor="let h of u.cols" [innerHTML]="h"></th></tr></thead>
        <tbody>
          <tr *ngFor="let c of u.cases">
            <td><span [innerHTML]="c.uc"></span><span *ngIf="c.done" class="badge">built</span></td>
            <td *ngFor="let v of c.vals" [innerHTML]="v"></td>
          </tr>
        </tbody>
      </table>
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
    .uc { margin:.4rem 0 1.25rem; }
    .uc-h { font-weight:700; color:#4c1d95; margin:.7rem 0 .25rem; font-size:1.05rem; }
    .uc-table { font-size:.92rem; }
    .uc-table th:first-child, .uc-table td:first-child { white-space:nowrap; }
    .uc-table td { color:#344054; }
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
    { pattern: 'ReAct', cols: ['<b>Re</b> — Reasoning (the Thought)', '<b>Act</b> — Acting (the tool call)'], cases: [
      { uc: '<b>Smart link discovery</b>', done: true, vals: ['judge which fetched links are real vehicle resources worth keeping', 'call <code>fetch_page</code> on the seed, then on the chosen links'] },
      { uc: '<b>Single-model deep-dive</b>', vals: ['decide the next page to open (spec → trims → pricing) from what it has read', 'fetch that next page'] },
      { uc: '<b>Recall / safety lookup</b>', vals: ['decide which result is the relevant recall for the model-year', 'search NHTSA / fetch the recall page'] },
      { uc: '<b>Dealer / inventory locator</b>', vals: ['decide the next form field / link to reach local stock', 'submit the dealer search / open results'] },
      { uc: '<b>Broken-link repair</b>', vals: ['infer where the page moved from the 404 + site structure', 'search the site / fetch candidate URLs'] },
    ]},
    { pattern: 'Plan-and-Execute', cols: ['<b>Plan</b> — all steps up front', '<b>Execute</b> — run each (+ re-plan)'], cases: [
      { uc: '<b>Multi-brand comparison search</b>', done: true, vals: ['decompose into one sub-query per brand × facet', 'retrieve each, merge + dedup, synthesize'] },
      { uc: '<b>Buyer\'s-guide builder</b>', vals: ['candidates → specs → price → safety → rank', 'run each step; re-plan if a candidate lacks data'] },
      { uc: '<b>Adaptive company onboarding</b>', vals: ['discover → ingest → index per site', 'run each; re-plan to a Playwright crawl for JS sites'] },
      { uc: '<b>Spec-sheet assembly</b>', vals: ['one retrieval per spec dimension', 'fetch each dimension, assemble the table'] },
      { uc: '<b>Total-cost-of-ownership report</b>', vals: ['price, MPG, maintenance, insurance, resale sub-queries', 'retrieve each, compute the total'] },
    ]},
    { pattern: 'ReWOO', cols: ['<b>Re</b> — Reasoning (plan all calls blind)', '<b>WOO</b> — WithOut Observation (run all, no feedback)'], cases: [
      { uc: '<b>Batch spec enrichment</b>', vals: ['plan every fetch call for the model list in one pass', 'run all fetches in parallel; a solver merges — no per-step LLM'] },
      { uc: '<b>Parallel multi-brand facts</b>', vals: ['plan the N facts × M brands queries up front', 'execute them all blind, combine at the end'] },
      { uc: '<b>Nightly price refresh</b>', vals: ['plan the price-fetch list for tracked models', 'execute LLM-free, store the results'] },
      { uc: '<b>Bulk image alt-text</b>', vals: ['plan a caption task per image up front', 'caption all in parallel — no observation between'] },
      { uc: '<b>Fixed-dimension comparison</b>', vals: ['plan all retrievals (towing/mpg/price/seats) at once', 'run them blind; solver synthesizes'] },
    ]},
    { pattern: 'Reflection / Reflexion', cols: ['<b>Generate</b>', '<b>Reflect</b> — self-critique', '<b>Revise</b>'], cases: [
      { uc: '<b>Answer quality gate</b>', vals: ['draft the answer from the sources', 'critic checks grounding + on-topic', 'regenerate / withhold if it fails'] },
      { uc: '<b>Chunk quality review</b>', vals: ['chunk the content', 'critique coherence / self-containment', 're-chunk the bad ones'] },
      { uc: '<b>Citation verification</b>', vals: ['answer with citations', 'check each claim maps to a source', 'drop / fix unsupported claims'] },
      { uc: '<b>Crawl coverage self-check</b>', vals: ['the discovered link set', '"did I miss EV / trucks?"', 'trigger a targeted re-crawl'] },
      { uc: '<b>Spec-extraction accuracy</b>', vals: ['extract the specs', 'verify vs the raw page', 'correct the mismatches'] },
    ]},
    { pattern: 'Tree of Thoughts (ToT)', cols: ['<b>Branch</b> — thoughts', '<b>Evaluate</b> — score', '<b>Search</b> — backtrack / pick'], cases: [
      { uc: '<b>"Best car for me"</b>', vals: ['different priority weightings (budget / space / efficiency)', 'score each candidate set', 'pick the best, prune weak paths'] },
      { uc: '<b>Ambiguous-query disambiguation</b>', vals: ['interpretations of "fast Toyota"', 'match each to intent + evidence', 'choose the best interpretation'] },
      { uc: '<b>Trim / option optimizer</b>', vals: ['trim + option combinations', 'score vs the budget / feature target', 'backtrack dead ends'] },
      { uc: '<b>Multi-constraint filter</b>', vals: ['candidate vehicles per constraint subset', 'check constraint satisfaction', 'prune, find a fit'] },
      { uc: '<b>Spec-conflict resolver</b>', vals: ['hypotheses (year / trim / market)', 'test each vs the sources', 'settle on the explanation'] },
    ]},
    { pattern: 'Router / dispatcher', cols: ['<b>Classify</b> — the signal', '<b>Route</b> — to the handler'], cases: [
      { uc: '<b>Compound-vs-simple routing</b>', done: true, vals: ['compound vs simple (keywords / brands / facets)', 'plan-execute vs langgraph'] },
      { uc: '<b>Framework router</b>', done: true, vals: ['framework name in the URL', 'langgraph / crewai / llamaindex / haystack'] },
      { uc: '<b>Query-type router</b>', vals: ['spec / where-to-buy / recall / price', 'vector search / dealer tool / safety source / pricing index'] },
      { uc: '<b>Store router</b>', vals: ['which store fits (company, modality)', 'pgVector / MongoDB / a company index'] },
      { uc: '<b>Topic / guardrail router</b>', vals: ['off-topic / vehicle / unsafe', 'refuse / pipeline / block'] },
    ]},
    { pattern: 'RAG pipeline', cols: ['<b>Retrieve</b>', '<b>Generate</b>'], cases: [
      { uc: '<b>Single-fact vehicle Q&amp;A</b>', done: true, vals: ['top-k chunks for the question', 'LLM answer over the chunks + citations'] },
      { uc: '<b>Company-scoped FAQ</b>', vals: ['chunks filtered to one brand', 'answer within that brand'] },
      { uc: '<b>Brochure / PDF lookup</b>', vals: ['chunks from ingested brochures', 'answer with brochure citations'] },
      { uc: '<b>"Explain this feature"</b>', vals: ['feature descriptions across models', 'summarize'] },
      { uc: '<b>Snapshot-grounded answer</b>', vals: ['chunks from one crawl snapshot', 'answer from that snapshot only'] },
    ]},
    { pattern: 'Multi-agent (supervisor / workers)', cols: ['<b>Supervisor</b> — delegate', '<b>Workers</b> — specialists', '<b>Merge</b>'], cases: [
      { uc: '<b>Researcher + advisor crew</b>', done: true, vals: ['the sequential crew orchestrates', 'researcher gathers, advisor answers', 'advisor composes the final answer'] },
      { uc: '<b>Per-brand workers</b>', vals: ['dispatch one worker per brand', 'brand researchers gather facts', 'supervisor merges into a comparison'] },
      { uc: '<b>Onboarding crew</b>', vals: ['coordinate the pipeline', 'crawler / extractor / indexer agents', 'an indexed corpus'] },
      { uc: '<b>Review aggregator</b>', vals: ['assign the sources', 'per-source review pullers', 'consensus synthesis'] },
      { uc: '<b>Spec / price / safety specialists</b>', vals: ['compose the report', 'spec / price / safety agents', 'the buyer\'s report'] },
    ]},
    { pattern: 'Evaluator-optimizer', cols: ['<b>Generate</b>', '<b>Evaluate</b> — judge', '<b>Optimize</b> — loop'], cases: [
      { uc: '<b>Answer refiner</b>', vals: ['draft the answer', 'judge completeness + citations', 'regenerate until it passes'] },
      { uc: '<b>Chunking optimizer</b>', vals: ['chunks with given params', 'retrieval quality on sample queries', 'tune params, repeat'] },
      { uc: '<b>Query rewriter</b>', vals: ['a search query', 'is the retrieval relevant?', 'rewrite until good'] },
      { uc: '<b>Summary tightener</b>', vals: ['a summary', 'accuracy + length vs source', 'shorten / fix, repeat'] },
      { uc: '<b>Embedding-model selector</b>', vals: ['embeddings per candidate model', 'score on labeled queries', 'pick the winner'] },
    ]},
    { pattern: 'Prompt chaining / parallelization', cols: ['<b>Step / Fan-out</b>', '<b>Merge / Hand-off</b>'], cases: [
      { uc: '<b>Multi-provider answer fan-out</b>', done: true, vals: ['ask N LLMs the same question in parallel', 'compare the answers side by side'] },
      { uc: '<b>Ingestion chain</b>', done: true, vals: ['fetch → clean → extract title → hash', 'store the record (hand to indexing)'] },
      { uc: '<b>Sectioning</b>', vals: ['summarize each brochure section in parallel', 'stitch the sections together'] },
      { uc: '<b>Voting</b>', vals: ['N models answer the same spec question', 'take the majority answer'] },
      { uc: '<b>Translate-then-index</b>', vals: ['translate non-English content → chunk', 'embed + store'] },
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
