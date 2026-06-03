import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { CompanyService } from '../../core/company.service';
import { CompResourceService } from '../../core/resource.service';
import { Company, CompanyResource } from '../../core/models';

@Component({
  selector: 'vkp-resources',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, DialogModule, TagModule, InputTextModule],
  template: `
  <h1 class="vkp-page-title">Companies <span class="vkp-muted">› Resources</span></h1>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">Company</label>
      <select [(ngModel)]="companyId" (ngModelChange)="load()"
              style="padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px; min-width:240px;">
        <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
      </select>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
      <p-button label="Add Resource" icon="pi pi-plus" (onClick)="openCreate()" [disabled]="!companyId"></p-button>
    </div>

    <div *ngIf="message" class="vkp-alert-ok">{{ message }}</div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>

    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 15" [rows]="15" [tableStyle]="{ 'min-width': '52rem' }">
      <ng-template pTemplate="header">
        <tr><th style="width:14rem">Name</th><th>Link</th><th style="width:8rem">Type</th><th style="width:7rem">Status</th><th style="width:8rem">Actions</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-r>
        <tr>
          <td><b>{{ r.resourceName }}</b></td>
          <td><a [href]="r.resourceLink" target="_blank" rel="noopener" style="color:var(--vkp-brand-2);">{{ r.resourceLink }}</a></td>
          <td><p-tag [value]="r.resourceType || '—'" severity="info"></p-tag></td>
          <td><p-tag [value]="r.status || '—'" [severity]="r.status === 'ACTIVE' ? 'success' : 'secondary'"></p-tag></td>
          <td>
            <p-button icon="pi pi-pencil" [text]="true" (onClick)="openEdit(r)" title="Edit"></p-button>
            <p-button icon="pi pi-trash" [text]="true" severity="danger" (onClick)="remove(r)" title="Delete"></p-button>
          </td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="5" class="vkp-muted" style="text-align:center; padding:1.5rem;">
          No resources for this company yet. Use <b>Add Resource</b> to add a root website/link.
        </td></tr>
      </ng-template>
    </p-table>
  </div>

  <p-dialog [(visible)]="showDialog" [modal]="true" [style]="{ width: '36rem' }" [header]="editing ? 'Edit Resource' : 'Add Resource'">
    <div style="display:flex; flex-direction:column; gap:1rem; padding-top:.5rem;">
      <div class="vkp-field"><label>Name</label><input pInputText [(ngModel)]="form.resourceName" placeholder="e.g. Chevrolet" /></div>
      <div class="vkp-field"><label>Link</label><input pInputText [(ngModel)]="form.resourceLink" placeholder="https://example.com" /></div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
        <div class="vkp-field"><label>Type</label><input pInputText [(ngModel)]="form.resourceType" placeholder="WEBSITE" /></div>
        <div class="vkp-field"><label>Status</label><input pInputText [(ngModel)]="form.status" placeholder="ACTIVE" /></div>
      </div>
    </div>
    <ng-template pTemplate="footer">
      <p-button label="Cancel" [text]="true" (onClick)="showDialog=false"></p-button>
      <p-button [label]="editing ? 'Save' : 'Create'" icon="pi pi-check" (onClick)="submit()"
                [disabled]="!form.resourceName.trim() || !form.resourceLink.trim()"></p-button>
    </ng-template>
  </p-dialog>
  `
})
export class ResourcesComponent implements OnInit {
  companies: Company[] = [];
  companyId = '';
  rows: CompanyResource[] = [];
  loading = false;
  message = '';
  error = '';

  showDialog = false;
  editing = false;
  editingId = '';
  form: CompanyResource = this.blank();

  constructor(private companySvc: CompanyService, private svc: CompResourceService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => {
        this.companies = rows;
        if (rows.length && rows[0].companyId) { this.companyId = rows[0].companyId; this.load(); }
      },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
  }

  blank(): CompanyResource {
    return { resourceName: '', resourceLink: '', resourceType: 'WEBSITE', status: 'ACTIVE' };
  }

  load(): void {
    if (!this.companyId) { this.rows = []; return; }
    this.loading = true; this.error = '';
    this.svc.list(this.companyId).subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load resources (is company-service on :8081 running?).'; this.loading = false; }
    });
  }

  openCreate(): void { this.editing = false; this.editingId = ''; this.form = this.blank(); this.message = ''; this.showDialog = true; }

  openEdit(r: CompanyResource): void {
    this.editing = true; this.editingId = r.companyResourceId ?? ''; this.message = '';
    this.form = { resourceName: r.resourceName, resourceLink: r.resourceLink, resourceType: r.resourceType, status: r.status };
    this.showDialog = true;
  }

  submit(): void {
    const op = this.editing
      ? this.svc.update(this.companyId, this.editingId, this.form)
      : this.svc.create(this.companyId, this.form);
    op.subscribe({
      next: () => { this.showDialog = false; this.message = this.editing ? 'Resource updated.' : 'Resource created.'; this.load(); },
      error: () => this.error = 'Save failed.'
    });
  }

  remove(r: CompanyResource): void {
    if (!r.companyResourceId || !confirm(`Delete resource "${r.resourceName}"?`)) { return; }
    this.svc.remove(this.companyId, r.companyResourceId).subscribe({
      next: () => { this.message = 'Resource deleted.'; this.load(); },
      error: () => this.error = 'Delete failed.'
    });
  }
}
