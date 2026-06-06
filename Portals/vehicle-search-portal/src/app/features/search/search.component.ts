import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { ExploreService, ProviderAnswer, ProviderInfo, SearchResponse, VectorStore } from '../../core/explore.service';
import { FlowDiagramComponent } from '../../shared/flow-diagram.component';

@Component({
  selector: 'vs-search',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, FlowDiagramComponent],
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
      <label class="vs-ctrl vs-check" title="Show the request flow diagram (what ran: embed, retrieve, LLM, guardrails…)">
        <input type="checkbox" [(ngModel)]="includeDiagram" name="includeDiagram" /> Include flow diagram
      </label>
    </div>

    <div class="vs-providers-pick" *ngIf="useLlm && providerList.length">
      <span class="vs-pick-label">LLM providers:</span>
      <label class="vs-pick" *ngFor="let p of providerList" [title]="p.model">
        <input type="checkbox" [checked]="selectedProviders.has(p.id)" (change)="toggleProvider(p.id)" />
        {{ p.label }}<span class="vs-free" *ngIf="p.free">free</span>
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
      <!-- Flow diagram (when 'Include flow diagram' is checked) -->
      <div class="vs-flow-card" *ngIf="response.steps?.length">
        <div class="vs-flow-head">
          <span><i class="pi pi-sitemap"></i> Request flow — what ran</span>
          <a *ngIf="response.logId" [routerLink]="['/logs', response.logId]" class="vs-flow-link">full log →</a>
        </div>
        <vs-flow-diagram [steps]="response.steps!"></vs-flow-diagram>
      </div>

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
              <span class="vs-tok" *ngIf="a.ok && a.totalTokens" title="LLM token usage (input / output)">
                {{ a.promptTokens }} in · {{ a.completionTokens }} out
              </span>
              <span class="vs-tok" *ngIf="a.ok && a.costUsd != null" title="Estimated cost (USD)">{{ cost(a) }}</span>
              <span class="vs-lat">{{ a.latencyMs }} ms</span>
            </span>
          </button>
          <div class="vs-acc-body" *ngIf="open.has(i)">
            <p *ngIf="a.ok" class="vs-snippet" style="margin:0">{{ a.answer }}</p>
            <p *ngIf="!a.ok" class="vs-acc-err" [title]="a.errorDetail || ''">
              <i class="pi pi-exclamation-triangle"></i> {{ a.error }}
            </p>
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

      <div class="vs-feedback" *ngIf="response.count > 0">
        <span>Was this helpful?</span>
        <button class="vs-fb" [class.on]="feedbackGiven === 'up'" [disabled]="!!feedbackGiven" (click)="rate('up')" title="Helpful">
          <i class="pi pi-thumbs-up"></i>
        </button>
        <button class="vs-fb" [class.on]="feedbackGiven === 'down'" [disabled]="!!feedbackGiven" (click)="rate('down')" title="Not helpful">
          <i class="pi pi-thumbs-down"></i>
        </button>
        <span class="vs-fb-thanks" *ngIf="feedbackGiven">Thanks for the feedback!</span>
      </div>

      <div class="vs-count" *ngIf="response.count > 0">
        {{ response.count }} source(s) for “{{ response.query }}”
        <a *ngIf="response.logId" [routerLink]="['/logs', response.logId]" class="vs-loglink">· view request log →</a>
      </div>

      <article class="vs-card" *ngFor="let r of response.results.slice(0, sourceLimit)">
        <div class="vs-card-head">
          <a [href]="r.sourceUrl" target="_blank" rel="noopener" class="vs-src">{{ hostOf(r.sourceUrl) }}</a>
          <span class="vs-score"
                [title]="'Semantic similarity between your query and this passage (vector cosine score) — higher = closer in meaning, not a keyword match'">
            {{ (r.score * 100) | number:'1.0-0' }}% match
          </span>
        </div>
        <p class="vs-snippet">{{ r.snippet }}</p>
        <a [href]="r.sourceUrl" target="_blank" rel="noopener" class="vs-link">{{ r.sourceUrl }} <i class="pi pi-external-link"></i></a>
      </article>

      <button type="button" class="vs-more" *ngIf="response.count > sourceLimit" (click)="sourceLimit = response.count">
        Show all {{ response.count }} sources
      </button>
      <button type="button" class="vs-more" *ngIf="response.count > defaultSourceLimit && sourceLimit >= response.count"
              (click)="sourceLimit = defaultSourceLimit">
        Show fewer
      </button>

      <div class="vs-empty" *ngIf="response.count === 0">
        No matching vehicle content found. Try different wording, or index more companies first.
      </div>
    </ng-container>
  </section>
  `,
  styles: [`
    .vs-flow-card { background:#fff; border:1px solid var(--vs-border); border-radius:14px; padding:1rem 1.1rem; margin-bottom:1rem;
      box-shadow:0 1px 2px rgba(124,58,237,.08), 0 10px 26px rgba(124,58,237,.1); }
    .vs-flow-head { display:flex; align-items:center; justify-content:space-between; font-weight:700; color:var(--vs-brand); margin-bottom:.7rem; }
    .vs-flow-head > span { display:flex; align-items:center; gap:.4rem; }
    .vs-flow-link, .vs-loglink { color:var(--vs-brand-2); font-weight:700; text-decoration:none; font-size:.82rem; }
    .vs-flow-link:hover, .vs-loglink:hover { text-decoration:underline; }
    .vs-loglink { margin-left:.4rem; }
  `]
})
export class SearchComponent implements OnInit, OnDestroy {
  query = '';
  store: VectorStore = 'pgvector';
  useLlm = true;
  includeDiagram = false;
  private nextOrigin: Record<string, any> | null = null;
  loading = false;
  error = '';
  response: SearchResponse | null = null;
  open = new Set<number>();   // expanded provider accordions
  private sub?: Subscription;

  providerList: ProviderInfo[] = [];
  // Default = free providers (Groq) so there's no cost and no error accordions unless opted in.
  selectedProviders = new Set<string>(['groq-70b', 'groq-8b']);

  readonly defaultSourceLimit = 5;
  sourceLimit = this.defaultSourceLimit;

  readonly examples = [
    'electric and hybrid vehicles',
    'all-wheel drive SUVs',
    'fuel economy and MPG'
  ];

  constructor(private explore: ExploreService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Provider checkboxes: load the available providers; default-check the free ones.
    this.explore.providers().subscribe({
      next: list => {
        this.providerList = list;
        const def = list.filter(p => p.default).map(p => p.id);
        if (def.length) { this.selectedProviders = new Set(def); }
      },
      error: () => {}
    });
    // State is driven by the URL query params, so the browser Back/Forward buttons move between
    // searches (and back to the landing page) — and a search is shareable/bookmarkable.
    this.sub = this.route.queryParamMap.subscribe(p => {
      this.store = (p.get('store') as VectorStore) || 'pgvector';
      this.useLlm = p.get('llm') !== 'false';
      this.includeDiagram = p.get('diagram') === 'true';
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

  feedbackGiven: 'up' | 'down' | null = null;

  toggleProvider(id: string): void {
    if (this.selectedProviders.has(id)) { this.selectedProviders.delete(id); } else { this.selectedProviders.add(id); }
  }

  rate(r: 'up' | 'down'): void {
    if (this.feedbackGiven) { return; }
    this.feedbackGiven = r;
    this.explore.feedback(r, this.response?.queryId, this.response?.sessionId).subscribe({ next: () => {}, error: () => {} });
  }

  cost(a: ProviderAnswer): string {
    return a.costUsd != null ? '$' + a.costUsd.toFixed(6) : '';
  }

  /** Pick an example and search it (origin recorded as the example-chip label). */
  pick(example: string): void {
    this.query = example;
    this.nextOrigin = { source: 'example-chip', label: example };
    this.run();
  }

  /** Run the current query — recorded in the URL so the browser Back button returns here. */
  run(): void {
    const q = this.query.trim();
    if (!q) { return; }
    if (!this.nextOrigin) { this.nextOrigin = { source: 'search-button', label: q }; }
    this.router.navigate([], { queryParams: { q, store: this.store, llm: this.useLlm, diagram: this.includeDiagram } });
  }

  /** Reset to the landing state (also a browser-history step). */
  clear(): void {
    this.router.navigate([], { queryParams: {} });
  }

  private execute(q: string): void {
    this.loading = true; this.error = ''; this.response = null; this.open.clear();
    this.sourceLimit = this.defaultSourceLimit;
    this.feedbackGiven = null;
    const providers = this.selectedProviders.size ? Array.from(this.selectedProviders) : undefined;
    const origin = this.nextOrigin || { source: 'url-deeplink', label: q };
    this.nextOrigin = null;
    origin['urlParams'] = { q, store: this.store, llm: String(this.useLlm), diagram: String(this.includeDiagram) };
    if (typeof document !== 'undefined') { origin['referrer'] = document.referrer || null; }
    this.explore.search(q, { store: this.store, useLlm: this.useLlm, topK: 8, providers, includeDiagram: this.includeDiagram, origin }).subscribe({
      next: r => {
        this.response = r;
        // Expand successful answers; collapse failed ones (a FAILED badge still shows on the header).
        const ok = r.answers.map((a, i) => ({ a, i })).filter(x => x.a.ok).map(x => x.i);
        this.open = new Set(ok.length ? ok : r.answers.map((_, i) => i));
        this.loading = false;
      },
      error: () => { this.error = 'Search is unavailable (is vehicle-explore-service on :8090 running?).'; this.loading = false; }
    });
  }

  hostOf(url: string): string {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
  }
}
