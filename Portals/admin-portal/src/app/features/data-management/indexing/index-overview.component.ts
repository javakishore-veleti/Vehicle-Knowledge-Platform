import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { IndexingService } from '../../../core/indexing.service';

@Component({
  selector: 'vkp-index-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Overview</span></h1>

  <div class="vkp-stats">
    <div class="vkp-stat"><div class="num">{{ workflows }}</div><div class="lbl">Indexing workflows</div></div>
    <div class="vkp-stat"><div class="num">{{ formulas }}</div><div class="lbl">Index formulas</div></div>
    <div class="vkp-stat"><div class="num">{{ credentials }}</div><div class="lbl">Provider credentials</div></div>
  </div>

  <div class="vkp-card">
    <h3 style="margin-top:0;">How indexing works</h3>
    <p class="vkp-muted" style="line-height:1.6;">
      Pick a company, a <b>workflow</b> (AIRFLOW DAG or SPRING_AI executor) and an <b>index formula</b>
      (embedding provider + model + chunking). The control plane dedups equivalent runs, then routes execution;
      the executor chunks the company's crawl snapshot, embeds it, and writes vectors into a per-model
      pgVector table. Each run is recorded in the <b>index logs</b> ledger.
    </p>
    <div class="vkp-toolbar">
      <a [routerLink]="['/data-management','data-indexing','trigger']"><p-button label="Trigger Indexing" icon="pi pi-bolt"></p-button></a>
      <a [routerLink]="['/data-management','data-indexing','workflows']"><p-button label="Workflows" [outlined]="true" icon="pi pi-bolt"></p-button></a>
      <a [routerLink]="['/data-management','data-indexing','formulas']"><p-button label="Formulas" [outlined]="true" icon="pi pi-sliders-h"></p-button></a>
      <a [routerLink]="['/data-management','data-indexing','logs']"><p-button label="Index Logs" [outlined]="true" icon="pi pi-list"></p-button></a>
    </div>
    <div *ngIf="error" class="vkp-alert-err" style="margin-top:1rem;">{{ error }}</div>
  </div>
  `
})
export class IndexOverviewComponent implements OnInit {
  workflows = 0;
  formulas = 0;
  credentials = 0;
  error = '';
  constructor(private svc: IndexingService) {}
  ngOnInit(): void {
    this.svc.workflows().subscribe({ next: r => this.workflows = r.length, error: () => this.error = 'Could not reach indexing-service on :8086.' });
    this.svc.formulas().subscribe({ next: r => this.formulas = r.length, error: () => {} });
    this.svc.credentials().subscribe({ next: r => this.credentials = r.length, error: () => {} });
  }
}
