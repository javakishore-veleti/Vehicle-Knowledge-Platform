import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Architecture → Data Management → Pipelines.
 *  Explains Data Management (orchestrated pipeline) vs the AI Agents / Agent Roster (interactive lab). */
@Component({
  selector: 'app-dm-pipelines',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Data Management pipelines vs the AI Agents roster</h2>
    <p class="lead">
      They touch the <b>same pipeline</b> but from <b>opposite ends</b>: one is the <i>production
      control plane</i>, the other is an <i>interactive lab</i>. They differ in <b>purpose,
      mechanism, scale, and persistence</b>.
    </p>

    <h3>Data Management — the orchestrated production pipeline</h3>
    <p>The <b>operational control plane</b> for the real, at-scale pipeline. Everything here runs
       through <b>Apache Airflow DAGs</b> (triggered via <code>airflow-adapter-service</code>) and
       <b>persists to the real stores</b>:</p>
    <table class="t">
      <thead><tr><th>Sub-section</th><th>What it does</th><th>DAG / store</th></tr></thead>
      <tbody>
        <tr><td><b>Data Collection</b></td><td>discover links from a company's seeds, crawl snapshots</td><td><code>vkp_discover_resources</code> → <code>company_resource_graph</code></td></tr>
        <tr><td><b>Data Ingestion</b></td><td>fetch each page's <b>actual content</b></td><td><code>vkp_process_resources</code> → <code>company_resource_content</code></td></tr>
        <tr><td><b>Data Indexing</b></td><td>embed content → vectors (formulas, creds, logs)</td><td><code>vkp_index_*</code> → <code>vkp_vectors.vec_*</code></td></tr>
        <tr><td><b>Guardrails</b></td><td>the query / safety ledger</td><td><code>user_queries_*</code></td></tr>
      </tbody>
    </table>
    <p>It's <b>batch, scheduled/triggered, stateful, recorded</b> (runs, ledgers, logs) — the way you'd
       actually populate the knowledge base for thousands of pages.</p>

    <h3>AI Agents (Agent Roster) — the interactive framework lab</h3>
    <p>A <b>playground to run one stage with one agent framework and see the result immediately</b>, via
       <b>live HTTP APIs</b> (<code>vehicle-explore-service</code> / <code>agentic-service</code>) —
       <b>no Airflow</b>:</p>
    <ul class="bullets">
      <li>Pick a <b>framework</b> (langgraph, crewai, … 8 total) × a <b>stage</b> (collect / index / search), hit <b>Run</b>.</li>
      <li>Synchronous, single-shot, returns JSON on screen.</li>
      <li><b>Dry-run by default</b> (collect doesn't persist unless <code>persist=true</code>).</li>
      <li>Purpose: <b>experiment with and compare</b> agent SDKs/patterns, debug a single step, learn the flow.</li>
    </ul>

    <h3>Same stages, different intent</h3>
    <table class="t">
      <thead><tr><th></th><th>Data Management</th><th>AI Agents (Roster)</th></tr></thead>
      <tbody>
        <tr><td><b>Mechanism</b></td><td>Airflow DAGs (orchestrated)</td><td>live FastAPI calls (single-shot)</td></tr>
        <tr><td><b>Purpose</b></td><td>run the real pipeline at scale</td><td>try/compare one framework on one stage</td></tr>
        <tr><td><b>Persistence</b></td><td>always writes the stores</td><td>preview by default (opt-in to persist)</td></tr>
        <tr><td><b>Scale / timing</b></td><td>batch, scheduled/triggered</td><td>one request, interactive</td></tr>
        <tr><td><b>Who / why</b></td><td>operators populating the KB</td><td>developers exploring agent frameworks</td></tr>
      </tbody>
    </table>

    <h3>So — same or different?</h3>
    <p class="frame">
      <b>Different aspects of the same conceptual stages.</b> Both deal with
      <b>collect → (ingest) → index → search</b>, but <b>Data Management = "do it for real, at scale,
      orchestrated"</b> and <b>AI Agents = "try one stage with a chosen agent framework, live."</b>
      They <i>can</i> write the same stores (the roster's collect can opt-in to persist into
      <code>company_resource_graph</code>, the same table the discover DAG fills) — which is why the
      <a routerLink="/agents/roster">Agent Roster</a> page explicitly contrasts itself with the Airflow
      DAG pipeline. Think of the Roster as the <b>interactive bench test</b> and Data Management as the
      <b>production assembly line</b> for the same work.
    </p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1040px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .lead { font-size:.96rem; line-height:1.6; color:#344054; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.84rem; }
    .arch .bullets { line-height:1.7; color:#344054; font-size:.92rem; }
    .t { border-collapse:collapse; width:100%; font-size:.9rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; }
    .arch .frame { background:#f7f9ff; border:1px solid #e0e7ff; border-left:3px solid #3538cd; border-radius:6px; padding:.75rem .95rem; font-size:.92rem; line-height:1.65; color:#344054; }
    .arch .frame a { color:#3538cd; }
  `]
})
export class DmPipelinesComponent {}
