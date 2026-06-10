import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { SECTION_DAGS, SECTION_LABELS } from '../../core/models';

const SECTION_BLURB: Record<string, string> = {
  'data-collection': 'Discovers links only from company resources (sitemaps, page/image/document URLs) and records them in the resource graph.',
  'data-ingestion': 'Crawls discovered links, fetches the actual content, and stores it for downstream indexing.',
  'data-indexing': 'Chunks and embeds extracted content, then routes it into the configured vector stores.'
};

const SECTION_MEANING: Record<string, string> = {
  'data-collection': 'Data Collection is the DISCOVERY stage. It finds which URLs exist for a company — ' +
    'sitemaps, page links, image and document URLs — and records them as a graph of links in ' +
    'company_resource_graph. It does NOT fetch page content (that is Data Ingestion). Think of it as ' +
    'building the table of contents / catalog of addresses.',
  'data-ingestion': 'Data Ingestion is the FETCH stage. It crawls each discovered link, downloads the ' +
    'page, and extracts clean text (+ a content hash) into company_resource_content, then triggers ' +
    'indexing. It answers "what does each link actually say?".',
  'data-indexing': 'Data Indexing chunks and embeds the extracted content and routes the vectors into ' +
    'the configured vector store(s) (pgVector / MongoDB), making the content semantically searchable.'
};

@Component({
  selector: 'vkp-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, ButtonModule],
  template: `
  <h1 class="vkp-page-title">{{ label }} <span class="vkp-muted">› Overview</span></h1>
  <div style="max-width:760px;">
    <details open class="ov-acc">
      <summary>What is {{ label }}?</summary>
      <div><p>{{ meaning }}</p></div>
    </details>
    <details class="ov-acc">
      <summary>Workflows</summary>
      <div>
        <p>{{ blurb }}</p>
        <p class="vkp-muted">Airflow DAG: <code>{{ dagId || 'not configured yet' }}</code></p>
        <a [routerLink]="['/data-management', section, 'workflows']">
          <p-button label="View Workflows" icon="pi pi-bolt"></p-button>
        </a>
      </div>
    </details>
  </div>
  `,
  styles: [`
    .ov-acc { border:1px solid #eaecf0; border-radius:8px; background:#fff; margin-bottom:.6rem; }
    .ov-acc > summary { cursor:pointer; padding:.65rem .9rem; font-weight:700; color:#1f2933; list-style:none; }
    .ov-acc > summary::-webkit-details-marker { display:none; }
    .ov-acc > summary:before { content:'▾'; margin-right:.5rem; color:#3538cd; }
    .ov-acc:not([open]) > summary:before { content:'▸'; }
    .ov-acc > div { padding:0 .9rem .85rem; color:#344054; font-size:.92rem; line-height:1.6; }
    .ov-acc code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.84rem; }
  `]
})
export class OverviewComponent implements OnInit, OnDestroy {
  section = 'data-collection';
  label = 'Data Collection';
  dagId = '';
  blurb = '';
  meaning = '';
  private sub?: Subscription;

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.sub = this.route.paramMap.subscribe(p => {
      this.section = p.get('section') ?? 'data-collection';
      this.label = SECTION_LABELS[this.section] ?? this.section;
      this.dagId = SECTION_DAGS[this.section] ?? '';
      this.blurb = SECTION_BLURB[this.section] ?? '';
      this.meaning = SECTION_MEANING[this.section] ?? this.blurb;
    });
  }

  ngOnDestroy(): void { this.sub?.unsubscribe(); }
}
