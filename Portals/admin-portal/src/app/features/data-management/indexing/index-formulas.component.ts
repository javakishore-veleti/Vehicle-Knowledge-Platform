import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { IndexingService, IndexFormula } from '../../../core/indexing.service';

@Component({
  selector: 'vkp-index-formulas',
  standalone: true,
  imports: [CommonModule, TableModule, TagModule, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Index Formulas</span></h1>
  <div class="vkp-card">
    <div class="vkp-toolbar">
      <span class="vkp-muted">An index formula = embedding provider + model + chunking params. The model decides the pgVector table.</span>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
    </div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>
    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 20" [rows]="20" [tableStyle]="{ 'min-width': '52rem' }">
      <ng-template pTemplate="header">
        <tr><th>Name</th><th style="width:11rem">Provider</th><th>Model</th><th>Params</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-f>
        <tr>
          <td><b>{{ f.name }}</b></td>
          <td><p-tag [value]="f.embeddingProvider" severity="info"></p-tag></td>
          <td style="font-family:monospace; font-size:.85rem">{{ f.embeddingModel }}</td>
          <td style="font-family:monospace; font-size:.8rem; color:var(--vkp-muted)">{{ f.params }}</td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="4" class="vkp-muted" style="text-align:center; padding:1.5rem;">No index formulas registered.</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class IndexFormulasComponent implements OnInit {
  rows: IndexFormula[] = [];
  loading = false;
  error = '';
  constructor(private svc: IndexingService) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.svc.formulas().subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load index formulas (is indexing-service on :8086 running?).'; this.loading = false; }
    });
  }
}
