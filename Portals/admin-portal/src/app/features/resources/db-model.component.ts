import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Architecture → Data Management → Database Model.
 *  ER diagram + per-table purpose / when populated (which workflow) / when read. */
@Component({
  selector: 'app-db-model',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Data Management — Database Model</h2>
    <p class="lead">
      The tables behind the pipeline and how a single resource flows through them:
      <b>companies → discovery → ingestion → indexing → vectors</b>. Each row below gives the table's
      <b>purpose</b>, <b>when it's populated</b> (by which workflow), and <b>when it's read</b>.
    </p>

    <a [href]="diagram" target="_blank" rel="noopener" title="Open full size">
      <img class="erd" [src]="diagram" alt="Data Management database model ER diagram" />
    </a>

    <h3>Tables &amp; lifecycle</h3>
    <table class="t">
      <thead><tr><th>Table (schema)</th><th>Purpose</th><th>Populated — by which workflow, when</th><th>Read — when</th></tr></thead>
      <tbody>
        <tr *ngFor="let r of tables">
          <td><b>{{ r.name }}</b><div class="sch">{{ r.schema }}</div></td>
          <td [innerHTML]="r.purpose"></td>
          <td [innerHTML]="r.populated"></td>
          <td [innerHTML]="r.read"></td>
        </tr>
      </tbody>
    </table>

    <p class="note"><b>⚠ Content retention / copyright:</b> <code>company_resource_content.clean_text</code>
       persists a copy of each page's extracted plain text (capped at ~20k chars). Crawling third-party
       sites and storing their text can implicate copyright depending on ownership, jurisdiction, and
       robots/ToS. The design is already defensible (respects robots.txt + delays; stores cleaned text not
       raw HTML; search returns snippets + citations + source links). To reduce exposure further, consider
       storing <b>embeddings + a short snippet + source URL only</b> (drop full text after embedding), plus
       retention/opt-out/takedown — see the <a routerLink="/resources/architecture/data-management/collection-vs-ingestion">Collection vs Ingestion</a> page.</p>

    <p class="foot">Schemas live in one <code>postgres</code> database, one <code>vkp_*</code> schema per
       service; <code>vkp_vectors.vec_*</code> uses the <b>pgvector</b> extension (or MongoDB Atlas Vector
       Search as a config-driven alternative). See <a routerLink="/resources/architecture/data-management/pipelines">Pipelines</a>.</p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1280px; }
    .arch h2 { margin: 0 0 .4rem; }
    .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.9rem; }
    .erd { width:100%; max-width:1340px; border:1px solid #eaecf0; border-radius:10px; background:#fff;
      box-shadow:0 1px 2px rgba(124,58,237,.08), 0 8px 24px rgba(124,58,237,.08); margin:.5rem 0 1rem; }
    .t { border-collapse:collapse; width:100%; font-size:.95rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.55rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; }
    .t tbody tr:hover { background:#faf8ff; }
    .t td:first-child { white-space:nowrap; }
    .t .sch { color:#94a3b8; font-size:.8rem; font-weight:400; }
    .arch .note { background:#fff7ed; border:1px solid #fde0b0; border-left:3px solid #f59e0b; border-radius:6px;
      padding:.75rem .95rem; font-size:1rem; line-height:1.65; color:#344054; }
    .arch .foot { color:#475467; font-size:.95rem; }
    .arch a { color:#3538cd; }
  `]
})
export class DbModelComponent {
  readonly diagram = '/images/arch-diagrams/db/data-management-db-model.svg';

  readonly tables = [
    { name: 'companies', schema: 'vkp_company',
      purpose: 'Master record of each company / brand to crawl.',
      populated: 'Admin creates them in <b>Companies</b> (Admin Portal) — manually, up front.',
      read: 'Everywhere downstream: discovery seeds, the crawl DAG (roots), portal dropdowns, search filters.' },
    { name: 'company_resources', schema: 'vkp_company',
      purpose: 'A company\'s seed / root resources (the root URLs to start from).',
      populated: 'Admin adds them under a company (<b>Companies → Resources</b>) — manually.',
      read: 'By discovery (<code>vkp_discover_resources</code>) and the crawl snapshot as the starting URLs.' },
    { name: 'company_resource_graph', schema: 'vkp_data_collection',
      purpose: 'Catalog of <b>discovered links</b> (page / image / document URLs) — the "map of what exists". Links only, no content.',
      populated: 'By <code>vkp_discover_resources</code> (Discovery) via <code>POST /graph/record</code> — when you run <b>Data Collection</b>.',
      read: 'By ingestion (the links to fetch), the Resource Graph UI, and indexing.' },
    { name: 'company_resource_content', schema: 'vkp_ingestion',
      purpose: 'Fetched + cleaned page <b>text</b> per link: <code>title</code>, <code>clean_text</code> (≤20k chars), <code>content_hash</code>.',
      populated: 'By <code>vkp_process_resources</code> (Ingestion) via <code>POST /content/record</code> — when you run <b>Data Ingestion</b>.',
      read: 'By indexing — the text it chunks + embeds. <i>(See the retention note below.)</i>' },
    { name: 'company_resource_vector_config', schema: 'vkp_vector_config',
      purpose: 'Which vector store(s) a resource indexes into (rule #3 — config-driven, never hardcoded).',
      populated: 'Admin configures it (or a default) — before indexing.',
      read: 'By indexing, to route embeddings to the configured store(s).' },
    { name: 'indexing_workflow', schema: 'vkp_indexing',
      purpose: 'Registry of indexing workflows (10k+), each with a <code>wf_type</code> (AIRFLOW | SPRING_AI) and a formula.',
      populated: 'Seeded / registered (admin or bootstrap).',
      read: 'By the indexing control plane when a run is triggered — it routes by <code>wf_type</code>.' },
    { name: 'index_formula', schema: 'vkp_indexing',
      purpose: 'The chunk/embed recipe: embedding model, dimensions, chunk size, overlap.',
      populated: 'Seeded / admin (<b>Index Formulas</b> UI).',
      read: 'By the indexing executor at embed time.' },
    { name: 'provider_credentials', schema: 'vkp_indexing',
      purpose: 'Embedding / LLM provider credentials for indexing (stored encrypted).',
      populated: 'Admin (<b>Provider Credentials</b> UI).',
      read: 'By the indexing executor when it calls the provider.' },
    { name: 'resource_graph_index_log', schema: 'vkp_indexing',
      purpose: 'The dedup / restart <b>ledger</b>: status per (company, workflow, formula): PENDING → IN_PROGRESS → COMPLETED / FAILED / SKIPPED / DEAD_LETTER.',
      populated: 'By the indexing control plane on trigger; updated by executor callbacks (<code>POST …/index-logs/{id}/callback</code>).',
      read: 'By the control plane (to dedup + restart) and the <b>Index Logs</b> UI.' },
    { name: 'vec_*  (embeddings)', schema: 'vkp_vectors · pgvector',
      purpose: 'The actual <b>embeddings</b>: chunk text + vector + metadata — what makes content semantically searchable.',
      populated: 'By the indexing executor (Spring AI <code>PgVectorStore</code> / the Python embed DAG) — the final indexing step.',
      read: 'By the <b>Search</b> stage (vehicle-explore-service retrieval) at query time.' },
  ];
}
