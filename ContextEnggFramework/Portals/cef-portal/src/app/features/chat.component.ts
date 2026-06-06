import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CefService } from '../core/cef.service';

interface Turn { who: 'user' | 'bot'; text: string; meta?: string; }

/** Customer context-aware vehicle chat — session persists so the Context Evolution loop carries
 *  memory across turns; each bot turn shows the context stats (retrieved/used/memory/strategies). */
@Component({
  selector: 'cef-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <h2>Context-Aware Vehicle Chat</h2>
  <div class="cfg">company <input [(ngModel)]="companyId" size="34"> · session <code>{{ sid }}</code></div>
  <div class="chat">
    <div *ngFor="let t of turns()" class="msg" [class.user]="t.who === 'user'" [class.bot]="t.who === 'bot'">
      <div class="bubble">{{ t.text }}</div>
      <div class="meta" *ngIf="t.meta">{{ t.meta }}</div>
    </div>
  </div>
  <form (ngSubmit)="send()">
    <input [(ngModel)]="q" name="q" placeholder="What hybrid SUVs does Toyota offer?" autocomplete="off">
    <button [disabled]="busy()">{{ busy() ? '…' : 'Send' }}</button>
  </form>
  `,
  styles: [`
    h2 { margin:.2rem 0; } .cfg { color:var(--muted); font-size:.8rem; margin-bottom:.5rem; }
    .cfg input { font-size:.8rem; padding:.2rem .4rem; border:1px solid #d0d5dd; border-radius:6px; }
    .chat { background:#fff; border:1px solid var(--line); border-radius:12px; min-height:48vh; padding:1rem; }
    .msg { margin:.6rem 0; } .msg.user { text-align:right; }
    .bubble { display:inline-block; padding:.55rem .8rem; border-radius:12px; max-width:90%; text-align:left; white-space:pre-wrap; }
    .user .bubble { background:var(--accent); color:#fff; } .bot .bubble { background:#f2f4f7; }
    .meta { font-size:.72rem; color:var(--muted); margin-top:.2rem; }
    form { display:flex; gap:.5rem; margin-top:.8rem; }
    form input { flex:1; padding:.6rem .8rem; border:1px solid #d0d5dd; border-radius:8px; }
    form button { padding:.6rem 1.1rem; background:var(--accent); color:#fff; border:none; border-radius:8px; cursor:pointer; }
  `]
})
export class ChatComponent {
  readonly sid = 'web-' + Math.random().toString(36).slice(2, 10);
  readonly turns = signal<Turn[]>([{ who: 'bot', text: 'Ask me about vehicles — I remember our conversation.' }]);
  readonly busy = signal(false);
  companyId = '10000000-0000-4000-8000-000000000004';
  q = '';

  constructor(private cef: CefService) {}

  send(): void {
    const query = this.q.trim(); if (!query) { return; }
    this.turns.update(t => [...t, { who: 'user', text: query }]);
    this.q = ''; this.busy.set(true);
    this.cef.orchestrate({ query, companyId: this.companyId, sessionId: this.sid, role: 'USER' }).subscribe({
      next: d => {
        const c = d.context || ({} as any);
        const meta = `retrieved ${c.retrieved} · used ${c.used} · memory ${c.memoryTurns} turns · ${(c.strategies || []).join('/')} · ${d.model} · ${d.latencyMs}ms`;
        this.turns.update(t => [...t, { who: 'bot', text: d.answer, meta }]);
        this.busy.set(false);
      },
      error: e => { this.turns.update(t => [...t, { who: 'bot', text: 'Error: ' + (e?.error?.detail ?? e?.message ?? e) }]); this.busy.set(false); }
    });
  }
}
