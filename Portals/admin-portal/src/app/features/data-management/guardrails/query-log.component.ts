import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { GuardrailsService, QueryLogRow } from '../../../core/guardrails.service';

@Component({
  selector: 'vkp-query-log',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, TagModule, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Guardrails <span class="vkp-muted">› Query Log</span></h1>
  <div class="vkp-card">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">User type</label>
      <select [(ngModel)]="userType" (ngModelChange)="load()"
              style="padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px;">
        <option value="">All</option>
        <option value="GUEST">Guest</option>
        <option value="AUTH">Authenticated</option>
      </select>
      <span class="vkp-muted">{{ rows.length }} recent quer(ies)</span>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
    </div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>
    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 20" [rows]="20" [tableStyle]="{ 'min-width': '60rem' }">
      <ng-template pTemplate="header">
        <tr>
          <th style="width:6rem">User</th><th>Query</th>
          <th style="width:8rem">Input</th><th style="width:8rem">Output</th>
          <th style="width:12rem">Session</th><th style="width:11rem">When</th>
        </tr>
      </ng-template>
      <ng-template pTemplate="body" let-q>
        <tr>
          <td><p-tag [value]="q.userType" [severity]="q.userType === 'AUTH' ? 'info' : 'secondary'"></p-tag></td>
          <td>{{ q.queryText }}</td>
          <td><p-tag [value]="q.inputAction || '—'" [severity]="verdict(q.inputAction)"></p-tag></td>
          <td><p-tag [value]="q.outputAction || '—'" [severity]="verdict(q.outputAction)"></p-tag></td>
          <td style="font-family:monospace; font-size:.78rem; color:var(--vkp-muted)">{{ q.sessionId }}</td>
          <td class="vkp-muted" style="font-size:.82rem">{{ q.createdDt }}</td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="6" class="vkp-muted" style="text-align:center; padding:1.5rem;">
          No queries logged yet (is guardrails-service on :8091 running?).
        </td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class QueryLogComponent implements OnInit {
  rows: QueryLogRow[] = [];
  userType = '';
  loading = false;
  error = '';

  constructor(private svc: GuardrailsService) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true; this.error = '';
    this.svc.recentQueries(this.userType, 200).subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load the query log (is guardrails-service on :8091 running?).'; this.loading = false; }
    });
  }

  verdict(action?: string | null): 'success' | 'warn' | 'danger' | 'secondary' {
    switch (action) {
      case 'allow': return 'success';
      case 'redact': case 'flag': return 'warn';
      case 'block': return 'danger';
      default: return 'secondary';
    }
  }
}
