import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { WorkflowService } from '../../core/workflow.service';
import { SECTION_DAGS, SECTION_LABELS, WorkflowRun } from '../../core/models';

const SECTION_WF: Record<string, string> = {
  'data-collection': 'This page lists and monitors runs of the <code>vkp_discover_resources</code> DAG — the ' +
    'DISCOVERY workflow. It crawls a company\'s seed links, extracts the links it finds (sitemaps, page / ' +
    'image / document URLs), and records them in the resource graph (<code>company_resource_graph</code>). ' +
    'Each row below is one DAG run and its state; use it to trigger and watch discovery jobs. It does ' +
    '<b>not</b> fetch page content — that is Data Ingestion.',
  'data-ingestion': 'This page lists and monitors runs of the <code>vkp_process_resources</code> DAG — the ' +
    'INGESTION workflow. It reads the discovered links, crawls each page, extracts clean text (+ a content ' +
    'hash) into <code>company_resource_content</code>, and then triggers indexing. Each row below is one DAG ' +
    'run and its state.',
  'data-indexing': 'This page lists and monitors runs of the indexing DAG, which chunks + embeds the extracted ' +
    'content and routes the vectors into the configured vector store(s) (<code>vkp_vectors</code>). Each row ' +
    'below is one DAG run and its state.'
};

@Component({
  selector: 'vkp-workflows',
  standalone: true,
  imports: [CommonModule, RouterLink, TableModule, ButtonModule, TagModule],
  template: `
  <h1 class="vkp-page-title">{{ label }} <span class="vkp-muted">› Workflows</span></h1>

  <details open class="vkp-explain">
    <summary>What is this?</summary>
    <div [innerHTML]="explain"></div>
  </details>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <div class="vkp-muted">Airflow DAG: <code>{{ dagId || '—' }}</code></div>
      <span class="vkp-spacer"></span>
      <a [routerLink]="['/data-management', section, 'overview']"><p-button label="Overview" [text]="true" icon="pi pi-info-circle"></p-button></a>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="reload()"></p-button>
    </div>

    <div *ngIf="error" style="background:#fde8e8; color:#9b1c1c; border:1px solid #f8b4b4; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem;">{{ error }}</div>

    <p-table [value]="runs" [loading]="loading" [paginator]="runs.length > 10" [rows]="10" [tableStyle]="{ 'min-width': '44rem' }">
      <ng-template pTemplate="header">
        <tr>
          <th>Run ID</th>
          <th>State</th>
          <th>Started</th>
          <th>Ended</th>
        </tr>
      </ng-template>
      <ng-template pTemplate="body" let-r>
        <tr>
          <td><code>{{ r.dagRunId }}</code></td>
          <td><p-tag [value]="r.state || 'unknown'" [severity]="stateSeverity(r.state)"></p-tag></td>
          <td>{{ r.startDate ? (r.startDate | date:'medium') : '—' }}</td>
          <td>{{ r.endDate ? (r.endDate | date:'medium') : '—' }}</td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="4" class="vkp-muted" style="text-align:center; padding:1.5rem;">
          No workflow runs yet for this section.
        </td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class WorkflowsComponent implements OnInit, OnDestroy {
  section = 'data-collection';
  label = 'Data Collection';
  dagId = '';
  explain = '';
  runs: WorkflowRun[] = [];
  loading = false;
  error = '';
  private sub?: Subscription;

  constructor(private route: ActivatedRoute, private svc: WorkflowService) {}

  ngOnInit(): void {
    this.sub = this.route.paramMap.subscribe(p => {
      this.section = p.get('section') ?? 'data-collection';
      this.label = SECTION_LABELS[this.section] ?? this.section;
      this.dagId = SECTION_DAGS[this.section] ?? '';
      this.explain = SECTION_WF[this.section] ?? '';
      this.reload();
    });
  }

  ngOnDestroy(): void { this.sub?.unsubscribe(); }

  reload(): void {
    if (!this.dagId) { this.runs = []; return; }
    this.loading = true;
    this.error = '';
    this.svc.list(this.dagId).subscribe({
      next: rows => { this.runs = rows; this.loading = false; },
      error: () => { this.error = 'Could not load workflows. Are airflow-adapter (:8083) and data-collection (:8084) running?'; this.loading = false; }
    });
  }

  stateSeverity(state?: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    switch (state) {
      case 'success': return 'success';
      case 'running':
      case 'queued': return 'info';
      case 'failed': return 'danger';
      default: return 'secondary';
    }
  }
}
