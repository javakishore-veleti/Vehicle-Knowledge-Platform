import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { CompanyService } from '../../core/company.service';
import { DiscoveryService } from '../../core/discovery.service';
import { Company, ResourceGraphNode } from '../../core/models';

@Component({
  selector: 'vkp-resource-graph',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TableModule, ButtonModule, DialogModule, TagModule, InputTextModule],
  template: `
  <h1 class="vkp-page-title">Data Collection <span class="vkp-muted">› Resource Graph</span></h1>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">Company</label>
      <select [(ngModel)]="selectedCompanyId" (ngModelChange)="loadGraph()"
              style="padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px; min-width:260px;">
        <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
      </select>
      <span class="vkp-spacer"></span>
      <a [routerLink]="['/data-management','data-collection','workflows']"><p-button label="Workflows" [text]="true" icon="pi pi-bolt"></p-button></a>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="loadGraph()"></p-button>
      <p-button label="Trigger Discovery" icon="pi pi-compass" (onClick)="openDiscover()" [disabled]="!selectedCompanyId"></p-button>
    </div>

    <div *ngIf="message" style="background:#e8f4ea; color:#1c5b2c; border:1px solid #b4dcc0; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem;">{{ message }}</div>
    <div *ngIf="error" style="background:#fde8e8; color:#9b1c1c; border:1px solid #f8b4b4; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem;">{{ error }}</div>

    <p-table [value]="nodes" [loading]="loading" [paginator]="nodes.length > 15" [rows]="15"
             [globalFilterFields]="['resourceUrl','resourceType','crawlStatus']" [tableStyle]="{ 'min-width': '48rem' }">
      <ng-template pTemplate="header">
        <tr><th>URL</th><th style="width:7rem">Type</th><th style="width:9rem">Crawl status</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-n>
        <tr>
          <td><a [href]="n.resourceUrl" target="_blank" rel="noopener" style="color:var(--vkp-brand-2);">{{ n.resourceUrl }}</a></td>
          <td><p-tag [value]="n.resourceType || '—'" [severity]="n.resourceType === 'SEED' ? 'info' : 'secondary'"></p-tag></td>
          <td><p-tag [value]="n.crawlStatus || '—'" [severity]="statusSeverity(n.crawlStatus)"></p-tag></td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="3" class="vkp-muted" style="text-align:center; padding:1.5rem;">
          No discovered resources yet. Use <b>Trigger Discovery</b> to crawl a seed URL.
        </td></tr>
      </ng-template>
    </p-table>
  </div>

  <p-dialog [(visible)]="showDialog" [modal]="true" [style]="{ width: '34rem' }" header="Trigger Discovery">
    <div style="display:flex; flex-direction:column; gap:1rem; padding-top:.5rem;">
      <div class="vkp-muted">Company: <b>{{ selectedCompanyName() }}</b></div>
      <div>
        <label style="display:block; margin-bottom:.35rem; font-weight:600;">Resource ID</label>
        <input pInputText [(ngModel)]="form.resourceId" style="width:100%" placeholder="e.g. r-1" />
      </div>
      <div>
        <label style="display:block; margin-bottom:.35rem; font-weight:600;">Seed URL</label>
        <input pInputText [(ngModel)]="form.seedUrl" style="width:100%" placeholder="https://example.com" />
      </div>
      <div class="vkp-muted" style="font-size:.85rem;">Crawls the seed for links and records them in the resource graph (runs as an Airflow DAG; refreshes here once it completes).</div>
    </div>
    <ng-template pTemplate="footer">
      <p-button label="Cancel" [text]="true" (onClick)="showDialog=false"></p-button>
      <p-button label="Discover" icon="pi pi-compass" (onClick)="submitDiscover()"
                [disabled]="!form.resourceId.trim() || !form.seedUrl.trim()"></p-button>
    </ng-template>
  </p-dialog>
  `
})
export class ResourceGraphComponent implements OnInit {
  companies: Company[] = [];
  selectedCompanyId = '';
  nodes: ResourceGraphNode[] = [];
  loading = false;
  message = '';
  error = '';

  showDialog = false;
  form = { resourceId: 'r-1', seedUrl: '' };

  constructor(private companySvc: CompanyService, private discoverySvc: DiscoveryService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => {
        this.companies = rows;
        if (rows.length && rows[0].companyId) { this.selectedCompanyId = rows[0].companyId; this.loadGraph(); }
      },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
  }

  loadGraph(): void {
    if (!this.selectedCompanyId) { this.nodes = []; return; }
    this.loading = true; this.error = '';
    this.discoverySvc.getGraph(this.selectedCompanyId).subscribe({
      next: rows => { this.nodes = rows; this.loading = false; },
      error: () => { this.error = 'Could not load the resource graph (is data-collection-service on :8084 running?).'; this.loading = false; }
    });
  }

  openDiscover(): void { this.message = ''; this.form = { resourceId: 'r-1', seedUrl: '' }; this.showDialog = true; }

  submitDiscover(): void {
    this.discoverySvc.discover(this.selectedCompanyId, this.form.resourceId.trim(), this.form.seedUrl.trim()).subscribe({
      next: res => {
        this.showDialog = false;
        this.message = `Discovery triggered (run ${res.dagRunId}). Refreshing the graph shortly…`;
        setTimeout(() => this.loadGraph(), 5000);
      },
      error: () => { this.error = 'Failed to trigger discovery.'; }
    });
  }

  selectedCompanyName(): string {
    return this.companies.find(c => c.companyId === this.selectedCompanyId)?.name ?? this.selectedCompanyId;
  }

  statusSeverity(status?: string): 'success' | 'info' | 'danger' | 'secondary' {
    switch (status) {
      case 'DISCOVERED': return 'success';
      case 'DISCOVERING': return 'info';
      case 'FAILED': return 'danger';
      default: return 'secondary';
    }
  }
}
