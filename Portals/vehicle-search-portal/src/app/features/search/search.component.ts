import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExploreService, SearchResponse, VectorStore } from '../../core/explore.service';

@Component({
  selector: 'vs-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <section class="vs-hero" [class.compact]="response || loading">
    <h1>Search vehicle knowledge</h1>
    <p class="vs-sub">Ask about models, features, pricing, electrification — across crawled automaker content.</p>
    <form class="vs-searchbar" (ngSubmit)="run()">
      <i class="pi pi-search"></i>
      <input [(ngModel)]="query" name="q" placeholder="e.g. electric and hybrid SUVs under $40,000" autocomplete="off" />
      <button type="submit" [disabled]="!query.trim() || loading">{{ loading ? 'Searching…' : 'Search' }}</button>
    </form>
    <div class="vs-controls">
      <label class="vs-ctrl">Vector store
        <select [(ngModel)]="store" name="store">
          <option value="pgvector">pgVector</option>
          <option value="mongodb">MongoDB</option>
        </select>
      </label>
      <label class="vs-ctrl vs-check">
        <input type="checkbox" [(ngModel)]="useLlm" name="useLlm" /> AI answer (LLM)
      </label>
    </div>

    <div class="vs-examples" *ngIf="!response && !loading">
      <span>Try:</span>
      <a *ngFor="let e of examples" (click)="query = e; run()">{{ e }}</a>
    </div>
  </section>

  <section class="vs-results" *ngIf="loading || response || error">
    <div *ngIf="error" class="vs-error">{{ error }}</div>

    <div *ngIf="loading" class="vs-skeleton">Searching the vehicle knowledge base…</div>

    <ng-container *ngIf="response && !loading">
      <div class="vs-answer" *ngIf="response.count > 0">
        <div class="vs-answer-label">
          <span><i class="pi pi-sparkles"></i> Answer</span>
          <span class="vs-badges">
            <span class="vs-badge" [class.ai]="response.answerSource === 'llm'">
              {{ response.answerSource === 'llm' ? 'AI-generated' : 'Extractive' }}
            </span>
            <span class="vs-badge store">{{ response.store === 'mongodb' ? 'MongoDB' : 'pgVector' }}</span>
          </span>
        </div>
        <p>{{ response.answer }}</p>
      </div>

      <div class="vs-count" *ngIf="response.count > 0">{{ response.count }} source(s) for “{{ response.query }}”</div>

      <article class="vs-card" *ngFor="let r of response.results">
        <div class="vs-card-head">
          <a [href]="r.sourceUrl" target="_blank" rel="noopener" class="vs-src">{{ hostOf(r.sourceUrl) }}</a>
          <span class="vs-score" [title]="'cosine similarity'">{{ (r.score * 100) | number:'1.0-0' }}% match</span>
        </div>
        <p class="vs-snippet">{{ r.snippet }}</p>
        <a [href]="r.sourceUrl" target="_blank" rel="noopener" class="vs-link">{{ r.sourceUrl }} <i class="pi pi-external-link"></i></a>
      </article>

      <div class="vs-empty" *ngIf="response.count === 0">
        No matching vehicle content found. Try different wording, or index more companies first.
      </div>
    </ng-container>
  </section>
  `
})
export class SearchComponent {
  query = '';
  store: VectorStore = 'pgvector';
  useLlm = true;
  loading = false;
  error = '';
  response: SearchResponse | null = null;

  readonly examples = [
    'electric and hybrid vehicles',
    'all-wheel drive SUVs',
    'fuel economy and MPG'
  ];

  constructor(private explore: ExploreService) {}

  run(): void {
    const q = this.query.trim();
    if (!q) { return; }
    this.loading = true; this.error = ''; this.response = null;
    this.explore.search(q, { store: this.store, useLlm: this.useLlm, topK: 6 }).subscribe({
      next: r => { this.response = r; this.loading = false; },
      error: () => { this.error = 'Search is unavailable (is vehicle-explore-service on :8090 running?).'; this.loading = false; }
    });
  }

  hostOf(url: string): string {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
  }
}
