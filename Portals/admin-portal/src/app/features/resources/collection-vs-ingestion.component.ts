import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Architecture → Data Management → Collection vs Ingestion.
 *  Clears up the common confusion between the discovery (links) and ingestion (content) stages. */
@Component({
  selector: 'app-collection-vs-ingestion',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Data Collection vs Data Ingestion</h2>
    <p class="lead">
      Not the same at all — they're <b>two distinct, sequential stages</b> (a load-bearing rule in VKP:
      <i>"Data Collection vs Ingestion are distinct"</i>). The confusion is understandable because both
      sub-sections have an <b>Overview</b> and a <b>Workflows</b> page — but each drives a <i>different</i>
      DAG over a <i>different</i> part of the pipeline.
    </p>

    <h3>The one-line difference</h3>
    <ul class="bullets">
      <li><b>Data Collection = find the LINKS</b> (discovery only — <i>which</i> URLs exist). <b>No page content.</b></li>
      <li><b>Data Ingestion = fetch the CONTENT</b> of those links (open each page, extract the actual text).</li>
    </ul>

    <h3>Side by side</h3>
    <table class="t">
      <thead><tr><th></th><th>Data Collection</th><th>Data Ingestion</th></tr></thead>
      <tbody>
        <tr><td><b>What it does</b></td><td>discovers <b>links only</b> — sitemaps, page links, image/doc URLs</td><td><b>crawls each discovered link</b>, fetches the page, extracts title + clean text (+ hash)</td></tr>
        <tr><td><b>Output (DB)</b></td><td><code>company_resource_graph</code> (a graph/map of URLs)</td><td><code>company_resource_content</code> (the actual extracted text)</td></tr>
        <tr><td><b>Service</b></td><td><code>data-collection-service</code> (:8084)</td><td><code>ingestion-service</code> (:8085)</td></tr>
        <tr><td><b>Airflow DAG</b></td><td><code>vkp_discover_resources</code></td><td><code>vkp_process_resources</code></td></tr>
        <tr><td><b>Then triggers</b></td><td>nothing (just records the link graph)</td><td><b>indexing</b> (embed the content → vectors)</td></tr>
      </tbody>
    </table>

    <h3>Analogy</h3>
    <ul class="bullets">
      <li><b>Data Collection</b> = building the <b>table of contents / catalog</b> — "here are all the
          pages and assets that exist on toyota.com." Just a list of addresses.</li>
      <li><b>Data Ingestion</b> = actually <b>opening each of those pages and extracting the text</b> so
          it can be indexed and searched.</li>
    </ul>

    <h3>The order</h3>
    <pre class="flow">Data Collection      →     Data Ingestion       →     Data Indexing
discover LINKS             fetch CONTENT              embed → vectors
(company_resource_graph)   (company_resource_content) (vkp_vectors.vec_*)</pre>

    <p class="frame">
      So: <b>Collection answers "what's there?" (URLs); Ingestion answers "what does it say?" (content).</b>
      You run Collection first to map the links, then Ingestion to pull the content of those links, then
      Indexing to make it searchable. <b>Why the deliberate split?</b> You can re-discover links cheaply
      without re-fetching all content, and re-ingest content for a known set of links without
      re-discovering — they have very different cost and frequency.
    </p>

    <p class="foot">See also <a routerLink="/resources/architecture/data-management/pipelines">Pipelines</a>
       and <a routerLink="/resources/architecture/data-management/interactive-lab">Interactive Lab</a>.</p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1040px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.92rem; }
    .arch .bullets { line-height:1.7; color:#344054; font-size:1.02rem; }
    .t { border-collapse:collapse; width:100%; font-size:.98rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; }
    .flow { background:#0c111d; color:#d1e0ff; padding:.8rem; border-radius:8px; font-size:.8rem; white-space:pre; overflow-x:auto; line-height:1.6; }
    .arch .frame { background:#f7f9ff; border:1px solid #e0e7ff; border-left:3px solid #3538cd; border-radius:6px; padding:.75rem .95rem; font-size:1.02rem; line-height:1.65; color:#344054; }
    .arch .foot { color:#475467; font-size:.98rem; }
    .arch a { color:#3538cd; }
  `]
})
export class CollectionVsIngestionComponent {}
