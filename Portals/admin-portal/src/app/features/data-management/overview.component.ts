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

@Component({
  selector: 'vkp-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, ButtonModule],
  template: `
  <h1 class="vkp-page-title">{{ label }} <span class="vkp-muted">› Overview</span></h1>
  <div class="vkp-card" style="max-width:760px;">
    <p style="margin-top:0;">{{ blurb }}</p>
    <p class="vkp-muted">Airflow DAG: <code>{{ dagId || 'not configured yet' }}</code></p>
    <a [routerLink]="['/data-management', section, 'workflows']">
      <p-button label="View Workflows" icon="pi pi-bolt"></p-button>
    </a>
  </div>
  `
})
export class OverviewComponent implements OnInit, OnDestroy {
  section = 'data-collection';
  label = 'Data Collection';
  dagId = '';
  blurb = '';
  private sub?: Subscription;

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.sub = this.route.paramMap.subscribe(p => {
      this.section = p.get('section') ?? 'data-collection';
      this.label = SECTION_LABELS[this.section] ?? this.section;
      this.dagId = SECTION_DAGS[this.section] ?? '';
      this.blurb = SECTION_BLURB[this.section] ?? '';
    });
  }

  ngOnDestroy(): void { this.sub?.unsubscribe(); }
}
