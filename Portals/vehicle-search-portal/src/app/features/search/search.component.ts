import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
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
      <button type="button" class="vs-clear" *ngIf="query || response || loading" (click)="clear()" title="Clear" aria-label="Clear search">
        <i class="pi pi-times"></i>
      </button>
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

    <div class="vs-examples" *ngIf="!loading">
      <span>Try:</span>
      <a *ngFor="let e of examples" (click)="pick(e)">{{ e }}</a>
    </div>
  </section>

  <section class="vs-results" *ngIf="loading || response || error">
    <div *ngIf="error" class="vs-error">{{ error }}</div>

    <div *ngIf="loading" class="vs-skeleton">Searching the vehicle knowledge base…</div>

    <ng-container *ngIf="response && !loading">
      <!-- Multi-provider comparison: one accordion per LLM provider -->
      <div class="vs-providers" *ngIf="response.count > 0 && response.answers.length">
        <div class="vs-providers-head">
          <span><i class="pi pi-sparkles"></i> AI answers — compare {{ response.answers.length }} provider(s)</span>
          <span class="vs-badge store">{{ response.store === 'mongodb' ? 'MongoDB' : 'pgVector' }}</span>
        </div>
        <div class="vs-acc" *ngFor="let a of response.answers; let i = index" [class.fail]="!a.ok">
          <button type="button" class="vs-acc-head" (click)="toggle(i)">
            <span class="vs-acc-title">
              <i class="pi" [ngClass]="open.has(i) ? 'pi-chevron-down' : 'pi-chevron-right'"></i>
              {{ a.label }}
            </span>
            <span class="vs-acc-meta">
              <span class="vs-badge" [ngClass]="a.ok ? 'ok' : 'err'">{{ a.ok ? 'OK' : 'FAILED' }}</span>
              <span class="vs-lat">{{ a.latencyMs }} ms</span>
            </span>
          </button>
          <div class="vs-acc-body" *ngIf="open.has(i)">
            <p *ngIf="a.ok" class="vs-snippet" style="margin:0">{{ a.answer }}</p>
            <p *ngIf="!a.ok" class="vs-acc-err">{{ a.error }}</p>
          </div>
        </div>
      </div>

      <!-- Single answer (extractive / LLM off) -->
      <div class="vs-answer" *ngIf="response.count > 0 && !response.answers.length">
        <div class="vs-answer-label">
          <span><i class="pi pi-sparkles"></i> Answer</span>
          <span class="vs-badges">
            <span class="vs-badge">Extractive</span>
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
export class SearchComponent implements OnInit, OnDestroy {
  query = '';
  store: VectorStore = 'pgvector';
  useLlm = true;
  loading = false;
  error = '';
  response: SearchResponse | null = null;
  open = new Set<number>();   // expanded provider accordions
  private sub?: Subscription;

  readonly examples = [
    'electric and hybrid vehicles',
    'all-wheel drive SUVs',
    'fuel economy and MPG'
  ];

  constructor(private explore: ExploreService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    // State is driven by the URL query params, so the browser Back/Forward buttons move between
    // searches (and back to the landing page) — and a search is shareable/bookmarkable.
    this.sub = this.route.queryParamMap.subscribe(p => {
      this.store = (p.get('store') as VectorStore) || 'pgvector';
      this.useLlm = p.get('llm') !== 'false';
      const q = (p.get('q') || '').trim();
      if (q) {
        this.query = q;
        this.execute(q);
      } else {
        this.query = ''; this.response = null; this.error = ''; this.loading = false; this.open.clear();
      }
    });
  }

  ngOnDestroy(): void { this.sub?.unsubscribe(); }

  toggle(i: number): void {
    if (this.open.has(i)) { this.open.delete(i); } else { this.open.add(i); }
  }

  /** Pick an example and search it. */
  pick(example: string): void {
    this.query = example;
    this.run();
  }

  /** Run the current query — recorded in the URL so the browser Back button returns here. */
  run(): void {
    const q = this.query.trim();
    if (!q) { return; }
    this.router.navigate([], { queryParams: { q, store: this.store, llm: this.useLlm } });
  }

  /** Reset to the landing state (also a browser-history step). */
  clear(): void {
    this.router.navigate([], { queryParams: {} });
  }

  private execute(q: string): void {
    this.loading = true; this.error = ''; this.response = null; this.open.clear();
    this.explore.search(q, { store: this.store, useLlm: this.useLlm, topK: 6 }).subscribe({
      next: r => { this.response = r; this.open = new Set(r.answers.map((_, i) => i)); this.loading = false; },
      error: () => { this.error = 'Search is unavailable (is vehicle-explore-service on :8090 running?).'; this.loading = false; }
    });
  }

  hostOf(url: string): string {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
  }
}
