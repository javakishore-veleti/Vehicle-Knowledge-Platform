import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { CompanyService } from '../../core/company.service';
import { CrawlService } from '../../core/crawl.service';
import { WorkflowService } from '../../core/workflow.service';
import { Company, WorkflowRun } from '../../core/models';

const CRAWL_DAG = 'vkp_crawl_company_snapshot';

@Component({
  selector: 'vkp-crawl',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TableModule, ButtonModule, TagModule, InputTextModule],
  template: `
  <h1 class="vkp-page-title">Data Collection <span class="vkp-muted">› Crawl Snapshot</span></h1>

  <div class="vkp-card" style="margin-bottom:1.25rem;">
    <div class="vkp-toolbar" style="flex-wrap:wrap;">
      <div>
        <label style="display:block;font-weight:600;margin-bottom:.3rem;">Company</label>
        <select [(ngModel)]="companyId" style="padding:.5rem;border:1px solid var(--vkp-border);border-radius:6px;min-width:240px;">
          <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
        </select>
      </div>
      <div>
        <label style="display:block;font-weight:600;margin-bottom:.3rem;">Max pages</label>
        <input type="number" min="1" [(ngModel)]="maxPages" style="width:120px;padding:.5rem;border:1px solid var(--vkp-border);border-radius:6px;" />
      </div>
      <div>
        <label style="display:block;font-weight:600;margin-bottom:.3rem;">Max depth</label>
        <input type="number" min="0" [(ngModel)]="maxDepth" style="width:120px;padding:.5rem;border:1px solid var(--vkp-border);border-radius:6px;" />
      </div>
      <span class="vkp-spacer"></span>
      <p-button label="Trigger Crawl" icon="pi pi-bolt" (onClick)="trigger()" [disabled]="!companyId || running"></p-button>
    </div>
    <div *ngIf="message" style="background:#e8f4ea;color:#1c5b2c;border:1px solid #b4dcc0;padding:.6rem .9rem;border-radius:6px;">{{ message }}</div>
    <div *ngIf="error" style="background:#fde8e8;color:#9b1c1c;border:1px solid #f8b4b4;padding:.6rem .9rem;border-radius:6px;">{{ error }}</div>
    <p class="vkp-muted" style="margin:.75rem 0 0;font-size:.85rem;">
      Runs a real (Playwright/Chromium) recursive crawl and stores a filesystem snapshot under
      <code>Crawling-Snapshot/&lt;Company&gt;/</code>. Large crawls run in the background — watch the runs below.
      Re-crawling a company that has a <code>__COMPLETED__</code> marker is skipped.
    </p>
  </div>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <h2 style="margin:0;font-size:1.1rem;">Crawl runs</h2>
      <span class="vkp-muted">(<code>{{ CRAWL_DAG }}</code>)</span>
      <span class="vkp-spacer"></span>
      <a [routerLink]="['/data-management','data-collection','graph']"><p-button label="Resource Graph" [text]="true" icon="pi pi-sitemap"></p-button></a>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="loadRuns()"></p-button>
    </div>
    <p-table [value]="runs" [loading]="loadingRuns" [paginator]="runs.length > 10" [rows]="10" [tableStyle]="{ 'min-width': '42rem' }">
      <ng-template pTemplate="header">
        <tr><th>Run ID</th><th>State</th><th>Started</th><th>Ended</th></tr>
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
        <tr><td colspan="4" class="vkp-muted" style="text-align:center;padding:1.5rem;">No crawl runs yet.</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class CrawlComponent implements OnInit {
  readonly CRAWL_DAG = CRAWL_DAG;
  companies: Company[] = [];
  companyId = '';
  maxPages = 1000;
  maxDepth = 100;
  running = false;
  message = '';
  error = '';
  runs: WorkflowRun[] = [];
  loadingRuns = false;

  constructor(private companySvc: CompanyService, private crawlSvc: CrawlService, private workflowSvc: WorkflowService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => { this.companies = rows; if (rows[0]?.companyId) { this.companyId = rows[0].companyId; } },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
    this.loadRuns();
  }

  loadRuns(): void {
    this.loadingRuns = true;
    this.workflowSvc.list(CRAWL_DAG).subscribe({
      next: r => { this.runs = r; this.loadingRuns = false; },
      error: () => { this.loadingRuns = false; }
    });
  }

  trigger(): void {
    this.message = ''; this.error = ''; this.running = true;
    this.crawlSvc.trigger(this.companyId, this.maxPages, this.maxDepth).subscribe({
      next: res => {
        this.running = false;
        this.message = `Crawl triggered (run ${res.dagRunId}, state ${res.state}). It runs in the background — refresh the runs to track it.`;
        setTimeout(() => this.loadRuns(), 3000);
      },
      error: () => { this.running = false; this.error = 'Failed to trigger crawl (are data-collection :8084 and the adapter :8083 running?).'; }
    });
  }

  stateSeverity(state?: string): 'success' | 'info' | 'danger' | 'secondary' {
    switch (state) {
      case 'success': return 'success';
      case 'running':
      case 'queued': return 'info';
      case 'failed': return 'danger';
      default: return 'secondary';
    }
  }
}
