import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

/** Resources → Design Patterns → Overview. The single narrative of the agent-patterns-service effort:
 *  every pattern × every framework × the 5 VKP use cases — what, why, architecture, progress, build log. */
@Component({
  selector: 'app-agent-patterns-overview',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="vkp-page arch">
    <h2>Agent Patterns Service — Overview</h2>
    <p class="lead">
      A production-grade harness that implements <b>every agentic pattern in every framework</b>, each runnable
      via one uniform API — plus the <b>5 concrete VKP use cases per pattern</b>. Built to <i>master each stack
      by seeing real, deployable code</i> side by side. This page is the whole story; the per-framework detail
      lives on the <a routerLink="/resources/design-patterns/langgraph">LangGraph</a> /
      <a routerLink="/resources/design-patterns/crewai">CrewAI</a> pages and the
      <a routerLink="/resources/mastery/map">Mastery Map</a>.
    </p>

    <nav class="toc">
      <div class="toc-title">Contents</div>
      <ol>
        <li><a (click)="go('s-what')">What &amp; why</a></li>
        <li><a (click)="go('s-arch')">Architecture</a></li>
        <li><a (click)="go('s-progress')">Progress at a glance</a></li>
        <li><a (click)="go('s-axes')">The two axes</a></li>
        <li><a (click)="go('s-usecases')">The 50 use cases (LangGraph)</a></li>
        <li><a (click)="go('s-run')">How to run</a></li>
        <li><a (click)="go('s-log')">Build log</a></li>
        <li><a (click)="go('s-links')">Where it lives</a></li>
      </ol>
    </nav>

    <h3 id="s-what">What &amp; why</h3>
    <p><b>Service:</b> <code>agent-patterns-service</code> (FastAPI, :8094). <b>Goal:</b> see exactly how each
       framework expresses each pattern, as professional code you can deploy — not toy snippets — and realize
       the project-specific use cases (recall lookup, dealer locator, spec-sheet assembly, …) on top.</p>

    <h3 id="s-arch">Architecture</h3>
    <ul class="bul">
      <li><b>Matrix layout:</b> <code>app/patterns/&lt;pattern&gt;/&lt;framework&gt;.py</code> — one cell per (pattern × framework), each self-registers into a central <b>registry</b>.</li>
      <li><b>Uniform contract:</b> <code>POST /agent-patterns/&#123;pattern&#125;/&#123;framework&#125;/run</code> · <code>GET /agent-patterns/patterns</code> (matrix) · <code>GET /agent-patterns/&#123;pattern&#125;/usecases</code> · <code>/health</code>.</li>
      <li><b>Use-case axis:</b> a <code>useCase</code> request field selects one of the 5 concrete VKP use cases per pattern.</li>
      <li><b>Lazy SDK imports:</b> the service boots with zero heavy SDKs; a cell imports its SDK only inside <code>run()</code>, so a missing SDK fails only that cell.</li>
      <li><b>Reproducible installs:</b> everything pinned in <code>requirements.txt</code> (<code>uv pip install -r</code>); venv on <b>Python 3.12</b>.</li>
    </ul>

    <h3 id="s-progress">Progress at a glance</h3>
    <div class="prog">
      <div class="pill done"><b>26 / 80</b> framework cells</div>
      <div class="pill done"><b>50 / 50</b> LangGraph use cases ✅</div>
      <div class="pill"><b>2</b> frameworks verified (LangGraph, CrewAI)</div>
      <div class="pill"><b>{{ patterns.length }}</b> patterns × <b>5</b> use cases</div>
    </div>
    <p class="muted">Framework axis: Reflection × 8 frameworks · LangGraph × 10 patterns · CrewAI × 10 patterns.
       Use-case axis: all 10 patterns × 5 use cases — complete in LangGraph, every one verified live.</p>

    <h3 id="s-axes">The two axes</h3>
    <table class="t">
      <thead><tr><th>Axis</th><th>What it is</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td><b>Pattern × Framework</b></td><td>how each <i>stack</i> expresses each <i>pattern</i> (the mechanics)</td><td>26 / 80</td></tr>
        <tr><td><b>Pattern × Use-case</b></td><td>the 5 concrete <i>VKP applications</i> of each pattern</td><td><b>50 / 50</b> (LangGraph)</td></tr>
      </tbody>
    </table>

    <h3 id="s-usecases">The 50 use cases <span class="dim">(all runnable in LangGraph ✓)</span></h3>
    <div class="uc" *ngFor="let p of patterns">
      <div class="uc-h"><b>{{ p.name }}</b> <code>{{ p.key }}</code></div>
      <div class="ucs"><span class="chip" *ngFor="let u of p.cases">{{ u }}</span></div>
    </div>

    <h3 id="s-run">How to run</h3>
    <pre class="code">cd Middleware/agent-patterns-service
uv pip install -r requirements.txt        # Python 3.12
export OPENAI_API_KEY=...                  # or GROQ_API_KEY=... (free)
uvicorn app.main:app --port 8094

curl -X POST localhost:8094/agent-patterns/reflection/langgraph/run \\
  -H 'content-type: application/json' -d '{{ '{' }}"input":"…","useCase":"chunk-quality-review"{{ '}' }}'</pre>

    <h3 id="s-log">Build log</h3>
    <ol class="log">
      <li *ngFor="let l of buildLog">{{ l }}</li>
    </ol>

    <h3 id="s-links">Where it lives</h3>
    <p class="foot">
      <a [href]="repo + '/Middleware/agent-patterns-service'" target="_blank" rel="noopener">agent-patterns-service</a>
      · <a [href]="repo + '/Middleware/agent-patterns-service/Development_Tracker.md'" target="_blank" rel="noopener">Development_Tracker.md</a>
      · <a routerLink="/resources/design-patterns/langgraph">LangGraph page</a>
      · <a routerLink="/resources/design-patterns/crewai">CrewAI page</a>
      · <a routerLink="/resources/design-patterns/agentic-patterns">Agentic Patterns</a>
      · <a routerLink="/resources/mastery/map">Mastery Map</a>.
    </p>
  </div>
  `,
  styles: [`
    .arch { padding: 1rem 1.5rem; max-width: 1100px; }
    .arch h2 { margin: 0 0 .4rem; } .arch h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .arch .dim { color:#94a3b8; font-weight:400; font-size:.9rem; }
    .arch .lead { font-size:1.06rem; line-height:1.6; color:#344054; }
    .arch .muted { color:#64748b; font-size:.92rem; }
    .arch code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.88rem; }
    .arch a { color:#3538cd; }
    .toc { background:#faf8ff; border:1px solid #e9e3fb; border-left:3px solid #7c3aed; border-radius:8px; padding:.7rem 1rem .8rem; margin:1rem 0 1.5rem; max-width:560px; }
    .toc-title { font-size:.74rem; letter-spacing:.08em; text-transform:uppercase; font-weight:700; color:#7b74a8; margin-bottom:.45rem; }
    .toc ol { margin:0; padding-left:1.4rem; } .toc li { margin:.26rem 0; font-size:.95rem; }
    .toc li::marker { color:#a855f7; font-weight:700; }
    .toc a { color:#3538cd; cursor:pointer; text-decoration:none; } .toc a:hover { text-decoration:underline; }
    .bul { line-height:1.7; color:#344054; font-size:.96rem; } .bul li { margin:.2rem 0; }
    .prog { display:flex; flex-wrap:wrap; gap:.6rem; margin:.4rem 0; }
    .pill { border-radius:20px; padding:.3rem .9rem; font-size:.92rem; border:1px solid #e2e8f0; background:#f8fafc; color:#475569; }
    .pill.done { background:#ecfdf3; color:#0f8a5f; border-color:#b7f0d2; }
    .t { border-collapse:collapse; width:100%; font-size:.93rem; margin:.5rem 0 1rem; }
    .t th, .t td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; vertical-align:top; }
    .t thead th { background:#f6f1ff; color:#4c1d95; } .t tbody tr:hover { background:#faf8ff; }
    .uc { margin:.3rem 0 .55rem; }
    .uc-h { font-weight:700; color:#4c1d95; margin:.45rem 0 .15rem; }
    .ucs { display:flex; flex-wrap:wrap; gap:.35rem; }
    .chip { font-size:.82rem; color:#0f8a5f; background:#ecfdf3; border:1px solid #b7f0d2; border-radius:12px; padding:.08rem .55rem; }
    .code { background:#0c111d; color:#d1e0ff; padding:.85rem; border-radius:8px; font-size:.82rem; white-space:pre-wrap; line-height:1.55; overflow-x:auto; }
    .log { line-height:1.65; color:#344054; font-size:.95rem; } .log li { margin:.25rem 0; }
    .arch .foot { color:#475467; font-size:.95rem; margin-top:.5rem; }
  `]
})
export class AgentPatternsOverviewComponent {
  readonly repo = 'https://github.com/javakishore-veleti/Vehicle-Knowledge-Platform/blob/main';

  go(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  readonly patterns = [
    { name: 'Reflection', key: 'reflection', cases: ['answer-quality-gate', 'chunk-quality-review', 'citation-verification', 'crawl-coverage-self-check', 'spec-extraction-accuracy'] },
    { name: 'ReAct', key: 'react', cases: ['smart-link-discovery', 'single-model-deep-dive', 'recall-safety-lookup', 'dealer-inventory-locator', 'broken-link-repair'] },
    { name: 'RAG pipeline', key: 'rag', cases: ['single-fact-qa', 'company-scoped-faq', 'brochure-pdf-lookup', 'explain-feature', 'snapshot-grounded'] },
    { name: 'Plan-and-Execute', key: 'plan-execute', cases: ['multi-brand-comparison', 'buyers-guide-builder', 'adaptive-onboarding', 'spec-sheet-assembly', 'tco-report'] },
    { name: 'Router / dispatcher', key: 'router', cases: ['compound-vs-simple', 'framework-router', 'query-type-router', 'store-router', 'topic-guardrail-router'] },
    { name: 'Prompt chaining / parallelization', key: 'chaining', cases: ['multi-provider-fanout', 'ingestion-chain', 'sectioning', 'voting', 'translate-then-index'] },
    { name: 'Multi-agent (supervisor / workers)', key: 'multi-agent', cases: ['researcher-advisor', 'per-brand-workers', 'onboarding-crew', 'review-aggregator', 'spec-price-safety'] },
    { name: 'Evaluator-optimizer', key: 'evaluator-optimizer', cases: ['answer-refiner', 'chunking-optimizer', 'query-rewriter', 'summary-tightener', 'embedding-model-selector'] },
    { name: 'ReWOO', key: 'rewoo', cases: ['batch-spec-enrichment', 'parallel-multi-brand-facts', 'nightly-price-refresh', 'bulk-image-alt-text', 'fixed-dimension-comparison'] },
    { name: 'Tree of Thoughts', key: 'tot', cases: ['best-car-for-me', 'ambiguous-query', 'trim-optimizer', 'multi-constraint-filter', 'spec-conflict-resolver'] },
  ];

  readonly buildLog = [
    'Scaffolded the FastAPI service (:8094) — registry, uniform run API, health/matrix, lazy SDK imports, Development_Tracker.',
    'Cycle 1 — Reflection across all 8 frameworks (LangGraph, CrewAI, LlamaIndex, Haystack, OpenAI Agents, Google ADK, MS Agent, AWS Strands); LangGraph verified live.',
    'Cycle 2 — LangGraph across all 10 patterns (ReAct, RAG, Plan-Execute, Router, Chaining, Multi-agent, Evaluator-optimizer, ReWOO, ToT), every one verified live.',
    'Recreated the venv on Python 3.12 (CrewAI lacks 3.14 wheels); installs moved to requirements.txt via uv.',
    'Cycle 3 — CrewAI across all 10 patterns, all verified live; reusable framework page + CrewAI page added.',
    'Use-case axis — added a useCase selector, then implemented + verified all 5 VKP use cases per pattern in LangGraph, one pattern per cycle: Reflection → RAG → Evaluator-optimizer → Router → Plan-Execute → Multi-agent → ReWOO → ToT → Chaining → ReAct.',
    'Result: 26/80 framework cells, and 50/50 use cases in LangGraph — all verified live.',
  ];
}
