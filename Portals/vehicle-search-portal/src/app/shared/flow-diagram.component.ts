import { Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlowStep } from '../core/explore.service';

/** Dependency-free flow diagram: renders ordered steps as color-coded nodes joined by arrows.
 *  Click a node to expand its detail. Used inline on the search page and on the log-detail page. */
@Component({
  selector: 'vs-flow-diagram',
  standalone: true,
  imports: [CommonModule],
  template: `
  <div class="flow">
    <ng-container *ngFor="let s of steps; let last = last">
      <button type="button" class="node" [attr.data-type]="s.type" [class.bad]="s.status==='error'||s.status==='blocked'"
              [class.skip]="s.status==='skip'" [class.open]="open()===s.n" (click)="toggle(s.n)">
        <span class="ico">{{ icon(s.type) }}</span>
        <span class="lbl">
          <b>{{ s.label }}</b>
          <small *ngIf="s.ms != null">{{ s.ms }} ms</small>
        </span>
        <span class="st" [attr.data-st]="s.status">{{ s.status }}</span>
      </button>
      <span class="arrow" *ngIf="!last">→</span>
    </ng-container>
  </div>

  <div class="detail" *ngIf="current() as s">
    <div class="dh"><span class="ico">{{ icon(s.type) }}</span> <b>{{ s.label }}</b> <span class="type">{{ s.type }}</span></div>
    <table>
      <tr *ngFor="let kv of entries(s.detail)"><td>{{ kv[0] }}</td><td>{{ fmt(kv[1]) }}</td></tr>
      <tr *ngIf="!entries(s.detail).length"><td colspan="2" class="empty">no extra detail</td></tr>
    </table>
  </div>
  `,
  styles: [`
    .flow { display:flex; flex-wrap:wrap; align-items:stretch; gap:.35rem; }
    .node {
      display:flex; align-items:center; gap:.5rem; text-align:left; cursor:pointer; font:inherit;
      background:#fff; border:1px solid var(--vs-border); border-left:4px solid var(--c,#a855f7);
      border-radius:12px; padding:.5rem .7rem; box-shadow:0 1px 2px rgba(124,58,237,.08); transition:transform .12s, box-shadow .12s;
    }
    .node:hover { transform:translateY(-1px); box-shadow:0 8px 20px rgba(124,58,237,.16); }
    .node.open { box-shadow:0 0 0 3px rgba(168,85,247,.25); }
    .node[data-type=request]   { --c:#6366f1; }
    .node[data-type=guardrail] { --c:#f59e0b; }
    .node[data-type=embed]     { --c:#7c3aed; }
    .node[data-type=retrieve]  { --c:#0ea5e9; }
    .node[data-type=llm]       { --c:#ec4899; }
    .node[data-type=store]     { --c:#10b981; }
    .node[data-type=answer]    { --c:#a855f7; }
    .node.bad { --c:#ef4444; background:#fff5f5; }
    .node.skip { opacity:.5; }
    .ico { font-size:1.05rem; }
    .lbl { display:flex; flex-direction:column; line-height:1.15; }
    .lbl b { font-size:.82rem; color:var(--vs-text); font-weight:700; }
    .lbl small { color:var(--vs-muted); font-size:.68rem; }
    .st { font-size:.6rem; font-weight:800; text-transform:uppercase; letter-spacing:.04em; padding:.08rem .4rem; border-radius:999px; background:#f1ecfe; color:#7c3aed; }
    .st[data-st=error], .st[data-st=blocked] { background:#fde8e8; color:#c0392b; }
    .st[data-st=skip] { background:#eef0f5; color:#94a3b8; }
    .arrow { align-self:center; color:#c4b5fd; font-weight:800; }
    .detail { margin-top:.7rem; background:#faf8ff; border:1px solid var(--vs-border); border-radius:12px; padding:.7rem .9rem; animation:vsrise .15s ease; }
    .dh { display:flex; align-items:center; gap:.4rem; margin-bottom:.4rem; }
    .dh .type { font-size:.66rem; font-weight:700; text-transform:uppercase; color:#a855f7; background:#f1ecfe; padding:.08rem .45rem; border-radius:999px; }
    .detail table { width:100%; border-collapse:collapse; font-size:.8rem; }
    .detail td { padding:.2rem .4rem; border-bottom:1px solid #efeafc; vertical-align:top; }
    .detail td:first-child { color:var(--vs-muted); font-weight:600; width:34%; }
    .detail .empty { color:var(--vs-muted); text-align:center; }
    @keyframes vsrise { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }
  `]
})
export class FlowDiagramComponent {
  @Input() steps: FlowStep[] = [];
  readonly open = signal<number>(-1);

  toggle(n: number): void { this.open.set(this.open() === n ? -1 : n); }
  current(): FlowStep | undefined { return this.steps.find(s => s.n === this.open()); }

  icon(type: string): string {
    return ({ request: '📥', guardrail: '🛡️', embed: '🧬', retrieve: '🔎', llm: '🤖', store: '💾', answer: '✅' } as Record<string, string>)[type] || '•';
  }
  entries(d?: Record<string, any>): [string, any][] {
    return Object.entries(d || {}).filter(([, v]) => v !== null && v !== undefined && v !== '');
  }
  fmt(v: any): string { return typeof v === 'object' ? JSON.stringify(v) : String(v); }
}
