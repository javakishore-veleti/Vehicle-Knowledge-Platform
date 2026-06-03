import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { CompanyService } from '../../../core/company.service';
import { IndexingService, IndexFormula, IndexWorkflow, ProviderCredential } from '../../../core/indexing.service';
import { Company, ResourceGraphNode } from '../../../core/models';

@Component({
  selector: 'vkp-trigger-index',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TableModule, TagModule, ButtonModule, CheckboxModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Trigger Indexing</span></h1>

  <div class="vkp-card">
    <div *ngIf="message" class="vkp-alert-ok">{{ message }}</div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>

    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:1rem;">
      <div class="vkp-field">
        <label>Company</label>
        <select [(ngModel)]="companyId" (ngModelChange)="onCompany()">
          <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
        </select>
      </div>
      <div class="vkp-field">
        <label>Workflow</label>
        <select [(ngModel)]="wfId">
          <option *ngFor="let w of workflows" [value]="w.wfId">{{ w.name }} ({{ w.wfType }})</option>
        </select>
      </div>
      <div class="vkp-field">
        <label>Index formula</label>
        <select [(ngModel)]="formulaId">
          <option *ngFor="let f of formulas" [value]="f.indexFormulaId">{{ f.name }} — {{ f.embeddingModel }}</option>
        </select>
      </div>
      <div class="vkp-field">
        <label>Provider credential <span class="vkp-muted">(optional)</span></label>
        <select [(ngModel)]="credentialId">
          <option value="">— default —</option>
          <option *ngFor="let c of credentials" [value]="c.providerCredentialId">{{ c.name }} ({{ c.providerType }})</option>
        </select>
      </div>
    </div>

    <div class="vkp-field">
      <label>Scope</label>
      <div style="display:flex; gap:1.5rem; align-items:center;">
        <label style="font-weight:400; display:flex; gap:.4rem; align-items:center;">
          <input type="radio" name="scope" value="WHOLE" [(ngModel)]="scope" /> Whole company
        </label>
        <label style="font-weight:400; display:flex; gap:.4rem; align-items:center;">
          <input type="radio" name="scope" value="SELECTED" [(ngModel)]="scope" /> Selected documents
        </label>
        <span class="vkp-muted" style="margin-left:.5rem;">
          <label style="font-weight:400; display:inline-flex; gap:.4rem; align-items:center;">
            <p-checkbox [(ngModel)]="force" [binary]="true"></p-checkbox> Force re-run (skip dedup)
          </label>
        </span>
      </div>
    </div>

    <!-- Document picker (SELECTED scope) -->
    <div *ngIf="scope === 'SELECTED'" style="margin-top:.5rem;">
      <div class="vkp-toolbar">
        <span class="vkp-muted">{{ docs.length }} registered snapshot page(s) · {{ selectedDocs.length }} selected</span>
        <span class="vkp-spacer"></span>
        <p-button label="Register snapshot pages" icon="pi pi-sync" [outlined]="true"
                  (onClick)="register()" [loading]="registering"></p-button>
      </div>
      <p-table [value]="docs" [(selection)]="selectedDocs" dataKey="resourceGraphId" [loading]="loadingDocs"
               [paginator]="docs.length > 10" [rows]="10" [tableStyle]="{ 'min-width': '48rem' }">
        <ng-template pTemplate="header">
          <tr><th style="width:3rem"><p-tableHeaderCheckbox></p-tableHeaderCheckbox></th><th>URL</th><th style="width:9rem">Crawl status</th></tr>
        </ng-template>
        <ng-template pTemplate="body" let-d>
          <tr>
            <td><p-tableCheckbox [value]="d"></p-tableCheckbox></td>
            <td><a [href]="d.resourceUrl" target="_blank" rel="noopener" style="color:var(--vkp-brand-2);">{{ d.resourceUrl }}</a></td>
            <td><p-tag [value]="d.crawlStatus || '—'" severity="secondary"></p-tag></td>
          </tr>
        </ng-template>
        <ng-template pTemplate="emptymessage">
          <tr><td colspan="3" class="vkp-muted" style="text-align:center; padding:1.25rem;">
            No registered pages. Click <b>Register snapshot pages</b> to turn this company's crawl snapshot into selectable docs.
          </td></tr>
        </ng-template>
      </p-table>
    </div>

    <div class="vkp-toolbar" style="margin-top:1.25rem;">
      <a [routerLink]="['/data-management','data-indexing','logs']"><p-button label="View Index Logs" [text]="true" icon="pi pi-list"></p-button></a>
      <span class="vkp-spacer"></span>
      <p-button label="Trigger Indexing" icon="pi pi-bolt" (onClick)="trigger()"
                [loading]="submitting" [disabled]="!canTrigger()"></p-button>
    </div>
  </div>
  `
})
export class TriggerIndexComponent implements OnInit {
  companies: Company[] = [];
  workflows: IndexWorkflow[] = [];
  formulas: IndexFormula[] = [];
  credentials: ProviderCredential[] = [];
  docs: ResourceGraphNode[] = [];
  selectedDocs: ResourceGraphNode[] = [];

  companyId = '';
  wfId = '';
  formulaId = '';
  credentialId = '';
  scope: 'WHOLE' | 'SELECTED' = 'WHOLE';
  force = false;

  loadingDocs = false;
  registering = false;
  submitting = false;
  message = '';
  error = '';

  constructor(private companySvc: CompanyService, private svc: IndexingService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => {
        this.companies = rows;
        if (rows.length && rows[0].companyId) { this.companyId = rows[0].companyId; this.onCompany(); }
      },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
    this.svc.workflows().subscribe({ next: r => { this.workflows = r; if (r.length) this.wfId = r[0].wfId; }, error: () => {} });
    this.svc.formulas().subscribe({ next: r => { this.formulas = r; if (r.length) this.formulaId = r[0].indexFormulaId; }, error: () => {} });
    this.svc.credentials().subscribe({ next: r => this.credentials = r, error: () => {} });
  }

  companyName(): string {
    return this.companies.find(c => c.companyId === this.companyId)?.name ?? '';
  }

  onCompany(): void {
    this.selectedDocs = [];
    this.loadDocs();
  }

  loadDocs(): void {
    if (!this.companyId) { this.docs = []; return; }
    this.loadingDocs = true;
    this.svc.snapshotDocs(this.companyId).subscribe({
      next: r => { this.docs = r; this.loadingDocs = false; },
      error: () => { this.docs = []; this.loadingDocs = false; }
    });
  }

  register(): void {
    if (!this.companyId) { return; }
    this.registering = true; this.message = ''; this.error = '';
    this.svc.registerSnapshot(this.companyId, this.companyName()).subscribe({
      next: r => {
        this.registering = false;
        this.message = `Registered ${r.registered} page(s) (${r.skipped} already present, ${r.total} total).`;
        this.loadDocs();
      },
      error: () => { this.registering = false; this.error = 'Registration failed (is the snapshot crawled and data-collection on :8084 running?).'; }
    });
  }

  canTrigger(): boolean {
    if (!this.companyId || !this.wfId || !this.formulaId || this.submitting) { return false; }
    return this.scope === 'WHOLE' || this.selectedDocs.length > 0;
  }

  trigger(): void {
    this.submitting = true; this.message = ''; this.error = '';
    const docIds = this.scope === 'SELECTED' ? this.selectedDocs.map(d => d.resourceGraphId) : undefined;
    this.svc.trigger(this.companyId, {
      wfId: this.wfId,
      indexFormulaId: this.formulaId,
      companyName: this.companyName(),
      providerCredentialId: this.credentialId || undefined,
      docIds,
      force: this.force,
      triggeredBy: 'admin-portal'
    }).subscribe({
      next: res => {
        this.submitting = false;
        this.message = res.deduped
          ? `Skipped — ${res.message} (log ${res.indexLogId}).`
          : `Indexing triggered (${res.wfType}, log ${res.indexLogId}, run ${res.runRef}). Watch progress in Index Logs.`;
      },
      error: () => { this.submitting = false; this.error = 'Failed to trigger indexing.'; }
    });
  }
}
