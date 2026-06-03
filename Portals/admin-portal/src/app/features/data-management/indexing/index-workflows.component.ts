import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { IndexingService, IndexWorkflow } from '../../../core/indexing.service';

@Component({
  selector: 'vkp-index-workflows',
  standalone: true,
  imports: [CommonModule, RouterLink, TableModule, TagModule, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Workflows</span></h1>
  <div class="vkp-card">
    <div class="vkp-toolbar">
      <span class="vkp-muted">The indexing workflow registry — each routes to an AIRFLOW DAG or a SPRING_AI executor.</span>
      <span class="vkp-spacer"></span>
      <a [routerLink]="['/data-management','data-indexing','trigger']"><p-button label="Trigger Indexing" icon="pi pi-bolt"></p-button></a>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
    </div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>
    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 20" [rows]="20" [tableStyle]="{ 'min-width': '52rem' }">
      <ng-template pTemplate="header">
        <tr><th style="width:7rem">Type</th><th>Name</th><th>Target</th><th style="width:7rem">Status</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-w>
        <tr>
          <td><p-tag [value]="w.wfType" [severity]="w.wfType === 'AIRFLOW' ? 'info' : 'success'"></p-tag></td>
          <td><b>{{ w.name }}</b><div class="vkp-muted" style="font-size:.8rem">{{ w.description }}</div></td>
          <td style="font-family:monospace; font-size:.85rem">{{ w.targetRef }}</td>
          <td><p-tag [value]="w.status || '—'" severity="secondary"></p-tag></td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="4" class="vkp-muted" style="text-align:center; padding:1.5rem;">No indexing workflows registered (is indexing-service on :8086 running?).</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class IndexWorkflowsComponent implements OnInit {
  rows: IndexWorkflow[] = [];
  loading = false;
  error = '';
  constructor(private svc: IndexingService) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.svc.workflows().subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load indexing workflows (is indexing-service on :8086 running?).'; this.loading = false; }
    });
  }
}
