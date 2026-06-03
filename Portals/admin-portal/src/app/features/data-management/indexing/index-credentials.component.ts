import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { IndexingService, ProviderCredential } from '../../../core/indexing.service';

@Component({
  selector: 'vkp-index-credentials',
  standalone: true,
  imports: [CommonModule, TableModule, TagModule, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Provider Credentials</span></h1>
  <div class="vkp-card">
    <div class="vkp-toolbar">
      <span class="vkp-muted">Embedding-provider and vector-store credentials (config is server-side only; never returned here).</span>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
    </div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>
    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 20" [rows]="20" [tableStyle]="{ 'min-width': '40rem' }">
      <ng-template pTemplate="header">
        <tr><th>Name</th><th style="width:14rem">Provider type</th><th style="width:8rem">Status</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-c>
        <tr>
          <td><b>{{ c.name }}</b></td>
          <td><p-tag [value]="c.providerType" severity="info"></p-tag></td>
          <td><p-tag [value]="c.status || '—'" severity="secondary"></p-tag></td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="3" class="vkp-muted" style="text-align:center; padding:1.5rem;">No provider credentials registered.</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class IndexCredentialsComponent implements OnInit {
  rows: ProviderCredential[] = [];
  loading = false;
  error = '';
  constructor(private svc: IndexingService) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.svc.credentials().subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load provider credentials (is indexing-service on :8086 running?).'; this.loading = false; }
    });
  }
}
