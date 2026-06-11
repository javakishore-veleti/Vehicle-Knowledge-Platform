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
        <li><a (click)="go('s-patterns')">The main alternative agent / orchestration patterns</a></li>
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

    <h3 id="s-patterns">The main alternative agent / orchestration patterns</h3>
    <table class="ap-table">
      <thead><tr><th>Pattern</th><th>Idea</th><th>One-liner</th><th>In VKP</th></tr></thead>
      <tbody>
        <tr *ngFor="let p of patterns" [class.react]="p.done">
          <td><b>{{ p.pattern }}</b></td><td>{{ p.idea }}</td><td>{{ p.oneliner }}</td>
          <td [innerHTML]="p.vkp"></td>
        </tr>
      </tbody>
    </table>

    <p class="frame">
      A useful framing (Anthropic's <i>Building Effective Agents</i>): <b>workflows</b> are deterministic
      graphs you design (prompt chaining, routing, parallelization, orchestrator-workers,
      evaluator-optimizer), while <b>agents</b> are autonomous loops where the model drives control
      flow — ReAct being the canonical agent loop.
    </p>

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
          <td><b>{{ r.fw }}</b></td><td [innerHTML]="r.how"></td><td><code>{{ r.file }}</code></td>
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
  `]
})
export class AgenticPatternsComponent {
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

  readonly patterns = [
    { pattern: 'ReAct', idea: 'reason ↔ act loop', oneliner: 'dynamically decide the next tool from observations (what collect uses)', done: true, vkp: '✅ collect · <code>langgraph</code>' },
    { pattern: 'Plan-and-Execute', idea: 'plan first, then do', oneliner: 'generate a full multi-step plan up front, execute each step, optionally re-plan', done: true, vkp: '✅ search · <code>plan-execute</code>' },
    { pattern: 'ReWOO', idea: 'plan tools without observations', oneliner: 'decide all tool calls in one shot to save tokens/latency, then run them', done: false, vkp: '—' },
    { pattern: 'Reflection / Reflexion', idea: 'self-critique', oneliner: 'produce output → critique it → revise; iterate to improve quality', done: false, vkp: '—' },
    { pattern: 'Tree of Thoughts (ToT)', idea: 'search over reasoning', oneliner: 'branch into multiple reasoning paths, score, backtrack — for hard problems', done: false, vkp: '—' },
    { pattern: 'Router / dispatcher', idea: 'classify then route', oneliner: 'pick the right tool/chain/sub-agent for the input (no loop needed)', done: true, vkp: '✅ <code>auto</code> router + <code>frameworks.run</code>' },
    { pattern: 'RAG pipeline', idea: 'retrieve → generate', oneliner: 'fixed graph: fetch context, then answer (no autonomous tool loop)', done: true, vkp: '✅ search · <code>langgraph</code> StateGraph' },
    { pattern: 'Multi-agent (supervisor / orchestrator-workers)', idea: 'delegate', oneliner: 'a supervisor splits work to specialized sub-agents that collaborate', done: true, vkp: '~ <code>crewai</code> sequential crews' },
    { pattern: 'Evaluator-optimizer', idea: 'generate ↔ judge', oneliner: 'one model produces, another grades/refines in a loop', done: false, vkp: '—' },
    { pattern: 'Prompt chaining / parallelization', idea: 'workflows', oneliner: 'deterministic step pipelines, or fan-out-then-merge (voting/sectioning)', done: true, vkp: '✅ crewai chains · multi-provider fan-out' },
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
