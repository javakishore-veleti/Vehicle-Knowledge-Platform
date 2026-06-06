import { Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlowStep } from '../core/cef.service';

/** Dependency-free flow diagram for the CEF pipeline: color-coded nodes joined by arrows; click a
 *  node to expand its self-explaining detail (desc + key/values, with long prompts/SQL in a block). */
@Component({
  selector: 'cef-flow-diagram',
  standalone: true,
  imports: [CommonModule],
  template: `
  <div class="flow">
    <ng-container *ngFor="let s of steps; let last = last">
      <button type="button" class="node" [attr.data-type]="s.type"
              [class.bad]="s.status==='error'||s.status==='blocked'" [class.open]="open()===s.n" (click)="toggle(s.n)">
        <span class="ico">{{ icon(s.type) }}</span>
        <span class="lbl"><b>{{ s.label }}</b><small *ngIf="s.ms != null">{{ s.ms }} ms</small></span>
        <span class="st" [attr.data-st]="s.status">{{ s.status }}</span>
      </button>
      <span class="arrow" *ngIf="!last">→</span>
    </ng-container>
  </div>

  <div class="detail" *ngIf="current() as s">
    <div class="dh"><span class="ico">{{ icon(s.type) }}</span> <b>{{ s.label }}</b> <span class="type">{{ s.type }}</span></div>
    <p class="sdesc" *ngIf="s.desc">{{ s.desc }}</p>
    <table>
      <tr *ngFor="let kv of entries(s.detail)">
        <td>{{ kv[0] }}</td>
        <td><pre *ngIf="isLong(kv[1]); else shortv">{{ fmt(kv[1]) }}</pre><ng-template #shortv>{{ fmt(kv[1]) }}</ng-template></td>
      </tr>
      <tr *ngIf="!entries(s.detail).length && !s.desc"><td colspan="2" class="empty">no extra detail</td></tr>
    </table>
  </div>
  `,
  styles: [`
    .flow { display:flex; flex-wrap:wrap; align-items:stretch; gap:.35rem; }
    .node { display:flex; align-items:center; gap:.5rem; text-align:left; cursor:pointer; font:inherit;
      background:#fff; border:1px solid var(--line); border-left:4px solid var(--c,#a855f7);
      border-radius:12px; padding:.5rem .7rem; box-shadow:var(--shadow-sm); transition:transform .12s, box-shadow .12s; }
    .node:hover { transform:translateY(-1px); box-shadow:var(--shadow); }
    .node.open { box-shadow:0 0 0 3px rgba(168,85,247,.25); }
    .node[data-type=request]    { --c:#6366f1; }
    .node[data-type=permission] { --c:#f59e0b; }
    .node[data-type=retrieve]   { --c:#0ea5e9; }
    .node[data-type=memory]     { --c:#14b8a6; }
    .node[data-type=assemble]   { --c:#7c3aed; }
    .node[data-type=reason]     { --c:#ec4899; }
    .node[data-type=evolve]     { --c:#22c55e; }
    .node[data-type=answer]     { --c:#a855f7; }
    .node[data-type=store]      { --c:#10b981; }
    .node.bad { --c:#ef4444; background:#fff5f5; }
    .ico { font-size:1.05rem; }
    .lbl { display:flex; flex-direction:column; line-height:1.15; }
    .lbl b { font-size:.82rem; color:var(--ink); font-weight:700; }
    .lbl small { color:var(--muted); font-size:.68rem; }
    .st { font-size:.6rem; font-weight:800; text-transform:uppercase; letter-spacing:.04em; padding:.08rem .4rem; border-radius:999px; background:#f1ecfe; color:#7c3aed; }
    .st[data-st=error], .st[data-st=blocked] { background:#fde8e8; color:#c0392b; }
    .arrow { align-self:center; color:#c4b5fd; font-weight:800; }
    .detail { margin-top:.7rem; background:#faf8ff; border:1px solid var(--line); border-radius:12px; padding:.7rem .9rem; }
    .dh { display:flex; align-items:center; gap:.4rem; margin-bottom:.4rem; }
    .dh .type { font-size:.66rem; font-weight:700; text-transform:uppercase; color:#a855f7; background:#f1ecfe; padding:.08rem .45rem; border-radius:999px; }
    .sdesc { margin:0 0 .6rem; color:var(--ink); font-size:.84rem; line-height:1.5; }
    .detail table { width:100%; border-collapse:collapse; font-size:.8rem; }
    .detail td { padding:.2rem .4rem; border-bottom:1px solid #efeafc; vertical-align:top; }
    .detail td:first-child { color:var(--muted); font-weight:600; width:30%; }
    .detail .empty { color:var(--muted); text-align:center; }
    .detail pre { margin:0; background:#2a1d52; color:#e9defb; padding:.5rem .6rem; border-radius:8px;
      font-size:.72rem; white-space:pre-wrap; word-break:break-word; max-height:280px; overflow:auto; }
  `]
})
export class FlowDiagramComponent {
  @Input() steps: FlowStep[] = [];
  readonly open = signal<number>(-1);

  toggle(n: number): void { this.open.set(this.open() === n ? -1 : n); }
  current(): FlowStep | undefined { return this.steps.find(s => s.n === this.open()); }

  icon(type: string): string {
    return ({ request: '📥', permission: '🔐', retrieve: '🔎', memory: '🧠', assemble: '🧩',
              reason: '🤖', evolve: '🔄', answer: '✅', store: '💾', guardrail: '🛡️' } as Record<string, string>)[type] || '•';
  }
  entries(d?: Record<string, any>): [string, any][] {
    return Object.entries(d || {}).filter(([, v]) => v !== null && v !== undefined && v !== '');
  }
  isLong(v: any): boolean { return typeof v === 'string' && (v.length > 60 || v.includes('\n')); }
  fmt(v: any): string { return typeof v === 'object' ? JSON.stringify(v, null, 2) : String(v); }
}
