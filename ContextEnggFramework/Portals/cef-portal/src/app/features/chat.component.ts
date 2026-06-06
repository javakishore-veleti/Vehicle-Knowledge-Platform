import { AfterViewChecked, Component, ElementRef, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CefService } from '../core/cef.service';

interface Ctx { retrieved: number; used: number; memoryTurns: number; strategies: string[]; model: string; latencyMs: number; }
interface Source { n: number; sourceUrl: string; score: number; }
interface Turn { who: 'user' | 'bot'; text: string; ctx?: Ctx; sources?: Source[]; }

/** Customer context-aware vehicle chat — session persists so the Context Evolution loop carries
 *  memory across turns; each bot turn shows the context stats (retrieved/used/memory/strategies)
 *  and the cited sources. */
@Component({
  selector: 'cef-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <section class="panel">
    <div class="panel-head">
      <div class="title">
        <h2>Context-Aware Vehicle Chat</h2>
        <p>Ask about vehicles — the assistant retrieves, remembers, and cites its sources.</p>
      </div>
      <div class="session"><span class="dot"></span> session <code>{{ sid }}</code></div>
    </div>

    <div class="toolbar">
      <label>Knowledge base</label>
      <select [(ngModel)]="companyId" name="company">
        <option *ngFor="let c of companies" [value]="c.id">{{ c.name }}</option>
      </select>
      <span class="hint">answers are scoped to this automaker's content</span>
    </div>

    <div class="stream" #stream>
      <div *ngFor="let t of turns()" class="row" [class.me]="t.who === 'user'">
        <div class="avatar" [class.bot]="t.who === 'bot'">{{ t.who === 'bot' ? '🧠' : '🙂' }}</div>
        <div class="col">
          <div class="bubble" [class.bot]="t.who === 'bot'">{{ t.text }}</div>
          <div class="chips" *ngIf="t.ctx as c">
            <span class="chip">🔎 retrieved {{ c.retrieved }}</span>
            <span class="chip ok">✅ used {{ c.used }}</span>
            <span class="chip">🧵 memory {{ c.memoryTurns }}</span>
            <span class="chip strat" *ngFor="let s of c.strategies">{{ s }}</span>
            <span class="chip model">{{ c.model }}</span>
            <span class="chip">⚡ {{ c.latencyMs }}ms</span>
          </div>
          <div class="sources" *ngIf="t.sources?.length">
            <a class="src" *ngFor="let s of t.sources" [href]="s.sourceUrl" target="_blank" rel="noopener" [title]="s.sourceUrl">
              <span class="n">{{ s.n }}</span>{{ host(s.sourceUrl) }}<small>{{ s.score | number:'1.2-2' }}</small>
            </a>
          </div>
        </div>
      </div>

      <div class="row" *ngIf="busy()">
        <div class="avatar bot">🧠</div>
        <div class="bubble bot typing"><i></i><i></i><i></i></div>
      </div>
    </div>

    <div class="suggest" *ngIf="turns().length <= 1 && !busy()">
      <button *ngFor="let s of suggestions" (click)="q = s; send()">{{ s }}</button>
    </div>

    <form class="composer" (ngSubmit)="send()">
      <input [(ngModel)]="q" name="q" placeholder="Ask about a vehicle…" autocomplete="off" [disabled]="busy()">
      <button type="submit" [disabled]="busy() || !q.trim()">{{ busy() ? '…' : 'Send' }}</button>
    </form>
  </section>
  `,
  styles: [`
    .panel {
      background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
      box-shadow:var(--shadow); display:flex; flex-direction:column; flex:1; overflow:hidden; min-height:68vh;
    }
    .panel-head { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; padding:1rem 1.25rem; background:var(--grad); color:#fff; }
    .panel-head h2 { margin:0; font-size:1.12rem; }
    .panel-head p { margin:.15rem 0 0; font-size:.82rem; opacity:.92; }
    .session { font-size:.74rem; opacity:.97; display:flex; align-items:center; gap:.4rem; white-space:nowrap; }
    .session code { background:rgba(255,255,255,.22); padding:.1rem .4rem; border-radius:6px; }
    .session .dot { width:8px; height:8px; border-radius:50%; background:#bbf7d0; box-shadow:0 0 0 3px rgba(187,247,208,.35); }

    .toolbar { display:flex; align-items:center; gap:.6rem; padding:.6rem 1.25rem; border-bottom:1px solid var(--line); background:#faf8ff; }
    .toolbar label { font-size:.72rem; font-weight:700; color:var(--accent2); text-transform:uppercase; letter-spacing:.04em; }
    .toolbar select { font-size:.85rem; font-weight:600; padding:.35rem .6rem; border:1px solid var(--line); border-radius:8px; color:var(--ink); background:#fff; cursor:pointer; }
    .toolbar select:focus { outline:none; border-color:var(--accent2); box-shadow:0 0 0 3px rgba(168,85,247,.18); }
    .toolbar .hint { font-size:.72rem; color:var(--muted); }

    .stream { flex:1; overflow-y:auto; padding:1.25rem; display:flex; flex-direction:column; gap:1rem; }
    .row { display:flex; gap:.7rem; align-items:flex-start; animation:cef-rise .18s ease; }
    .row.me { flex-direction:row-reverse; }
    .avatar { flex:none; width:34px; height:34px; border-radius:10px; display:grid; place-items:center; font-size:1rem; background:var(--grad-user); box-shadow:var(--shadow-sm); }
    .avatar.bot { background:var(--grad); }
    .col { display:flex; flex-direction:column; gap:.4rem; max-width:78%; }
    .row.me .col { align-items:flex-end; }
    .bubble {
      padding:.65rem .9rem; border-radius:14px; white-space:pre-wrap; word-break:break-word; font-size:.92rem;
      background:var(--grad-user); color:#fff; border-top-right-radius:4px; box-shadow:var(--shadow-sm);
    }
    .bubble.bot { background:#f5f2ff; color:var(--ink); border:1px solid var(--line); border-top-right-radius:14px; border-top-left-radius:4px; }
    .chips { display:flex; flex-wrap:wrap; gap:.35rem; }
    .chip { font-size:.68rem; font-weight:600; color:var(--accent); background:var(--accent-soft); border:1px solid #e9defb; padding:.12rem .5rem; border-radius:999px; }
    .chip.ok { color:#0f8a5f; background:#e7faf1; border-color:#c5f0db; }
    .chip.strat { color:#be185d; background:#fdeef6; border-color:#f9d7e8; }
    .chip.model { color:#6d28d9; background:#f1e9ff; border-color:#e4d4ff; }
    .sources { display:flex; flex-wrap:wrap; gap:.4rem; }
    .src {
      display:inline-flex; align-items:center; gap:.4rem; text-decoration:none; max-width:230px;
      font-size:.72rem; color:var(--ink); background:#fff; border:1px solid var(--line);
      padding:.2rem .55rem .2rem .2rem; border-radius:999px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
      box-shadow:var(--shadow-sm); transition:border-color .15s, transform .12s;
    }
    .src:hover { border-color:var(--accent2); transform:translateY(-1px); }
    .src .n { width:18px; height:18px; flex:none; border-radius:50%; background:var(--grad); color:#fff; font-size:.62rem; display:grid; place-items:center; }
    .src small { color:var(--faint); }

    .typing { display:inline-flex; gap:5px; align-items:center; }
    .typing i { width:7px; height:7px; border-radius:50%; background:var(--accent2); animation:cef-bounce 1.2s infinite; }
    .typing i:nth-child(2){ animation-delay:.15s } .typing i:nth-child(3){ animation-delay:.3s }

    .suggest { display:flex; flex-wrap:wrap; gap:.5rem; padding:0 1.25rem .25rem; }
    .suggest button { font-size:.8rem; color:var(--accent); background:var(--accent-soft); border:1px solid #e9defb; padding:.4rem .8rem; border-radius:999px; cursor:pointer; transition:transform .12s; }
    .suggest button:hover { transform:translateY(-1px); }

    .composer { display:flex; gap:.6rem; padding:1rem 1.25rem; border-top:1px solid var(--line); background:#faf8ff; }
    .composer input { flex:1; padding:.7rem .95rem; border:1px solid var(--line); border-radius:12px; font-size:.92rem; background:#fff; transition:border-color .15s, box-shadow .15s; }
    .composer input:focus { outline:none; border-color:var(--accent2); box-shadow:0 0 0 3px rgba(168,85,247,.18); }
    .composer button { padding:.7rem 1.3rem; background:var(--grad); color:#fff; border:none; border-radius:12px; font-weight:700; cursor:pointer; box-shadow:0 6px 16px rgba(124,58,237,.32); transition:opacity .15s, transform .12s; }
    .composer button:hover:not(:disabled) { transform:translateY(-1px); }
    .composer button:disabled { opacity:.55; cursor:default; box-shadow:none; }
  `]
})
export class ChatComponent implements AfterViewChecked {
  @ViewChild('stream') private streamEl?: ElementRef<HTMLElement>;
  private lastCount = 0;

  readonly sid = 'web-' + Math.random().toString(36).slice(2, 10);
  readonly turns = signal<Turn[]>([{ who: 'bot', text: 'Ask me about vehicles — I remember our conversation and cite my sources.' }]);
  readonly busy = signal(false);
  readonly suggestions = [
    'What hybrid SUVs does Toyota offer?',
    'Which is the most affordable?',
    'Compare their fuel economy',
  ];
  readonly companies = [
    { id: '10000000-0000-4000-8000-000000000004', name: 'Toyota' },
    { id: '10000000-0000-4000-8000-000000000001', name: 'General Motors' },
    { id: '10000000-0000-4000-8000-000000000002', name: 'Ford' },
    { id: '10000000-0000-4000-8000-000000000003', name: 'Honda' },
    { id: '10000000-0000-4000-8000-000000000005', name: 'BMW' },
  ];
  companyId = this.companies[0].id;
  q = '';

  constructor(private cef: CefService) {}

  ngAfterViewChecked(): void {
    const n = this.turns().length + (this.busy() ? 1 : 0);
    if (n !== this.lastCount && this.streamEl) {
      this.streamEl.nativeElement.scrollTop = this.streamEl.nativeElement.scrollHeight;
      this.lastCount = n;
    }
  }

  host(u: string): string { try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return u; } }

  send(): void {
    const query = this.q.trim(); if (!query || this.busy()) { return; }
    this.turns.update(t => [...t, { who: 'user', text: query }]);
    this.q = ''; this.busy.set(true);
    this.cef.orchestrate({ query, companyId: this.companyId, sessionId: this.sid, role: 'USER' }).subscribe({
      next: d => {
        const c = (d.context || {}) as any;
        const ctx: Ctx = {
          retrieved: c.retrieved, used: c.used, memoryTurns: c.memoryTurns,
          strategies: c.strategies || [], model: d.model, latencyMs: d.latencyMs,
        };
        this.turns.update(t => [...t, { who: 'bot', text: d.answer, ctx, sources: d.sources || [] }]);
        this.busy.set(false);
      },
      error: e => {
        this.turns.update(t => [...t, { who: 'bot', text: 'Error: ' + (e?.error?.detail ?? e?.message ?? e) }]);
        this.busy.set(false);
      }
    });
  }
}
