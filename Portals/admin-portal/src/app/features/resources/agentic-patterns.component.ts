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

    <h3>What ReAct is</h3>
    <p>The LLM runs a loop, interleaving <b>Thought → Action (tool call) → Observation</b>, until it has
       enough to answer:</p>
    <pre class="flow">Thought: I need the page's links  →  Action: fetch_page(seed)  →  Observation: {{ '{' }}links:[…]{{ '}' }}
Thought: these are the vehicle pages  →  Final answer: [JSON links]</pre>
    <p>That's exactly the <b>collect</b> stage in this codebase.</p>

    <h3>The main alternative agent / orchestration patterns</h3>
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

    <h3>How this maps to VKP</h3>
    <ul class="map">
      <li *ngFor="let m of mapping"><b>{{ m.k }}</b> → <span [innerHTML]="m.v"></span></li>
    </ul>
    <p class="foot">On the <a routerLink="/agents/roster">Agent Roster</a>, picking a different
       <b>framework</b> for a stage is effectively picking a different <b>agent implementation</b>
       (and sometimes a different pattern) behind the same endpoint.</p>
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
  `]
})
export class AgenticPatternsComponent {
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
