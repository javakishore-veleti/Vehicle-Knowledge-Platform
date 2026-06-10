import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Architecture → Data Management → Interactive Lab.
 *  Candid answer to: "are the agent frameworks actually used in production, or is the lab just for fun?" */
@Component({
  selector: 'app-interactive-lab',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Interactive Lab — are the agent frameworks used in production?</h2>
    <p class="lead">
      A fair challenge: if the production pipeline doesn't run the agent frameworks, is the
      <b>AI Agents / Agent Roster</b> "interactive lab" just for fun? Short answer: <b>no</b> — but you
      <i>have</i> spotted a real architectural seam. Here's the honest breakdown.
    </p>

    <h3>You're right about the DAGs</h3>
    <p>The production <b>collect / ingest / index</b> Airflow DAGs use <b>no agent frameworks at all</b>.
       They import only the standard library (<code>urllib</code>, <code>html.parser</code>,
       <code>json</code>) for crawling + link extraction, and <code>sentence-transformers</code> for
       embeddings. <b>Zero</b> LangGraph / CrewAI / MSAgent / etc. So for the <b>bulk ingestion
       pipeline</b>, your statement holds: the frameworks aren't used.</p>

    <h3>But it's not "just for fun" — two reasons</h3>
    <p><b>1. The SEARCH stage IS production, and it IS framework-based.</b> Search isn't a DAG — it's a
       <b>live API</b>. The <a routerLink="/agents/roster">Vehicle Search</a> path calls
       <code>/api/vehicle-explore/{{ '{' }}framework{{ '}' }}/search</code>, and <code>frameworks.run(...)</code>
       routes real customer queries through <b>langgraph</b> (default), crewai, llamaindex or haystack
       (<code>IMPLEMENTED = {{ '{' }}langgraph, crewai, llamaindex, haystack{{ '}' }}</code>). So the
       frameworks <b>do</b> run in production — for <i>search / answering</i>, just not for
       <i>crawling / indexing</i>.</p>
    <p><b>2. The agentic collect/index are a deliberate <i>alternative</i>, not the default — by design.</b>
       Bulk-crawling and embedding thousands of pages is exactly where you <b>don't</b> want an LLM agent:
       a deterministic crawler is faster, cheaper, and more reliable than asking an agent to discover
       links 10,000 times. Agents earn their keep on the <i>hard</i> cases (JS-heavy sites, semantic
       relevance filtering, messy content). So the split is intentional:</p>
    <table class="t">
      <thead><tr><th>Stage</th><th>Production default</th><th>Agent alternative</th></tr></thead>
      <tbody>
        <tr><td><b>collect / ingest / index</b></td><td><b>deterministic DAGs</b> (fast, cheap, reliable at scale)</td><td>the roster's agentic collect/index — can persist to the <i>same</i> stores (opt-in)</td></tr>
        <tr><td><b>search</b></td><td><b>framework-based</b> (langgraph) — already production</td><td>the roster lets you compare/swap frameworks</td></tr>
      </tbody>
    </table>

    <h3>So what's the lab actually for?</h3>
    <ul class="bullets">
      <li><b>Evaluate &amp; choose</b> — A/B the 8 frameworks to pick the search default, and to decide
          <i>whether</i> an agentic collect/index is worth promoting for a given site.</li>
      <li><b>Promote selectively</b> — the agentic-service is wired so a stage <i>can</i> persist to
          <code>company_resource_graph</code> / <code>vkp_vectors</code> (the same tables the DAGs fill).
          It's a one-config-step from lab to production for the cases that need it.</li>
      <li><b>Debug / onboard / demo</b> — run one stage on one input and read the JSON.</li>
    </ul>

    <h3>The honest gap</h3>
    <p class="note"><b>A genuine roadmap seam:</b> the agentic collect/index are <b>not yet wired into the
       ingestion DAGs</b>. That's a deliberate "deterministic for bulk, agentic-on-demand" stance — but
       if the goal were <i>agentic ingestion in production</i>, the next step would be having a DAG (or the
       ingestion-service) call the <code>agentic-service</code> / <code>vehicle-explore-service</code>
       collect/index endpoint instead of the stdlib crawler.</p>

    <p class="foot">See also <a routerLink="/resources/architecture/data-management/pipelines">Data Management
       Pipelines</a> (production control plane vs interactive lab) and the
       <a routerLink="/agents/roster">Agent Roster</a> itself.</p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1040px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .lead { font-size:.96rem; line-height:1.6; color:#344054; }
    .arch p { line-height:1.65; color:#344054; font-size:.92rem; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.84rem; }
    .arch .bullets { line-height:1.7; color:#344054; font-size:.92rem; }
    .t { border-collapse:collapse; width:100%; font-size:.9rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; }
    .arch .note { background:#fff7ed; border:1px solid #fde0b0; border-left:3px solid #f59e0b; border-radius:6px; padding:.7rem .95rem; font-size:.92rem; line-height:1.65; color:#344054; }
    .arch .foot { color:#475467; font-size:.9rem; }
    .arch a { color:#3538cd; }
  `]
})
export class InteractiveLabComponent {}
