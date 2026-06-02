import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Table, TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DialogModule } from 'primeng/dialog';
import { TagModule } from 'primeng/tag';
import { CompanyService } from '../../core/company.service';
import { Company } from '../../core/models';

@Component({
  selector: 'vkp-companies',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, InputTextModule, DialogModule, TagModule],
  template: `
  <h1 class="vkp-page-title">Companies</h1>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <span class="p-input-icon-left">
        <i class="pi pi-search"></i>
        <input pInputText type="text" placeholder="Search companies…"
               (input)="dt.filterGlobal($any($event.target).value, 'contains')" style="padding-left:2rem; min-width:280px;" />
      </span>
      <span class="vkp-spacer"></span>
      <p-button label="New Company" icon="pi pi-plus" (onClick)="openNew()"></p-button>
    </div>

    <div *ngIf="error" style="background:#fde8e8; color:#9b1c1c; border:1px solid #f8b4b4; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem;">{{ error }}</div>

    <p-table #dt [value]="companies" [loading]="loading" [paginator]="true" [rows]="10"
             [rowsPerPageOptions]="[10,25,50]" [globalFilterFields]="['name','status','description']"
             [tableStyle]="{ 'min-width': '40rem' }" dataKey="companyId">
      <ng-template pTemplate="header">
        <tr>
          <th pSortableColumn="name">Name <p-sortIcon field="name"></p-sortIcon></th>
          <th>Description</th>
          <th pSortableColumn="status">Status <p-sortIcon field="status"></p-sortIcon></th>
          <th pSortableColumn="updatedDt">Updated <p-sortIcon field="updatedDt"></p-sortIcon></th>
          <th style="width:8rem">Actions</th>
        </tr>
      </ng-template>
      <ng-template pTemplate="body" let-c>
        <tr>
          <td>{{ c.name }}</td>
          <td class="vkp-muted">{{ c.description || '—' }}</td>
          <td><p-tag [value]="c.status" [severity]="statusSeverity(c.status)"></p-tag></td>
          <td>{{ c.updatedDt ? (c.updatedDt | date:'medium') : '—' }}</td>
          <td>
            <p-button icon="pi pi-pencil" [text]="true" (onClick)="openEdit(c)" title="Edit"></p-button>
            <p-button icon="pi pi-trash" [text]="true" severity="danger" (onClick)="remove(c)" title="Delete"></p-button>
          </td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="5" class="vkp-muted" style="text-align:center; padding:1.5rem;">No companies yet.</td></tr>
      </ng-template>
    </p-table>
  </div>

  <p-dialog [(visible)]="showDialog" [modal]="true" [style]="{ width: '32rem' }"
            [header]="editing?.companyId ? 'Edit Company' : 'New Company'">
    <div style="display:flex; flex-direction:column; gap:1rem; padding-top:.5rem;">
      <div>
        <label style="display:block; margin-bottom:.35rem; font-weight:600;">Name</label>
        <input pInputText [(ngModel)]="form.name" style="width:100%" />
      </div>
      <div>
        <label style="display:block; margin-bottom:.35rem; font-weight:600;">Description</label>
        <input pInputText [(ngModel)]="form.description" style="width:100%" />
      </div>
      <div>
        <label style="display:block; margin-bottom:.35rem; font-weight:600;">Status</label>
        <select [(ngModel)]="form.status" style="width:100%; padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px;">
          <option value="ACTIVE">ACTIVE</option>
          <option value="INACTIVE">INACTIVE</option>
        </select>
      </div>
    </div>
    <ng-template pTemplate="footer">
      <p-button label="Cancel" [text]="true" (onClick)="showDialog=false"></p-button>
      <p-button label="Save" icon="pi pi-check" (onClick)="save()" [disabled]="!form.name.trim()"></p-button>
    </ng-template>
  </p-dialog>
  `
})
export class CompaniesComponent implements OnInit {
  @ViewChild('dt') dt!: Table;

  companies: Company[] = [];
  loading = false;
  error = '';

  showDialog = false;
  editing: Company | null = null;
  form: Company = { name: '', description: '', status: 'ACTIVE' };

  constructor(private svc: CompanyService) {}

  ngOnInit(): void { this.reload(); }

  reload(): void {
    this.loading = true;
    this.error = '';
    this.svc.list().subscribe({
      next: rows => { this.companies = rows; this.loading = false; },
      error: () => { this.error = 'Could not load companies. Is company-service running on :8081?'; this.loading = false; }
    });
  }

  openNew(): void {
    this.editing = null;
    this.form = { name: '', description: '', status: 'ACTIVE' };
    this.showDialog = true;
  }

  openEdit(c: Company): void {
    this.editing = c;
    this.form = { name: c.name, description: c.description, status: c.status ?? 'ACTIVE' };
    this.showDialog = true;
  }

  save(): void {
    const done = () => { this.showDialog = false; this.reload(); };
    const fail = () => { this.error = 'Save failed.'; };
    if (this.editing?.companyId) {
      this.svc.update(this.editing.companyId, this.form).subscribe({ next: done, error: fail });
    } else {
      this.svc.create(this.form).subscribe({ next: done, error: fail });
    }
  }

  remove(c: Company): void {
    if (!c.companyId || !confirm(`Delete "${c.name}"?`)) { return; }
    this.svc.remove(c.companyId).subscribe({ next: () => this.reload(), error: () => this.error = 'Delete failed.' });
  }

  statusSeverity(status?: string): 'success' | 'secondary' | 'danger' {
    if (status === 'ACTIVE') { return 'success'; }
    if (status === 'DELETED') { return 'danger'; }
    return 'secondary';
  }
}
