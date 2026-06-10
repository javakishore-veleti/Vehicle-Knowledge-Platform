import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

/** Resources → Tools → Pydantic. Reference page: what pydantic is, what it gives you, how VKP
 *  uses it, and exactly where in this codebase. */
@Component({
  selector: 'app-pydantic',
  standalone: true,
  imports: [CommonModule],
  template: `
  <div class="vkp-page tool">
    <h2>Pydantic</h2>
    <p class="lead">
      <b>Pydantic</b> is a Python <b>data-validation and parsing</b> library built on type hints. You
      declare a model with typed fields, and pydantic guarantees that any data you load into it is the
      right shape — coercing/validating it and raising clear errors when it isn't.
    </p>

    <h3>What it gives you</h3>
    <ol class="gives">
      <li><b>Validation</b> — checks types, required vs optional, and constraints; bad input → a precise error.</li>
      <li><b>Parsing / coercion</b> — turns raw JSON/dicts into typed Python objects (e.g. <code>"5"</code> → <code>int 5</code>).</li>
      <li><b>Defaults &amp; optionals</b> — declared inline, applied automatically.</li>
      <li><b>Serialization</b> — model → dict/JSON via <code>.model_dump()</code>.</li>
      <li><b>Self-documenting + IDE support</b> — the type hints drive autocomplete, type-checking, and auto-generated schemas.</li>
    </ol>

    <h3>How VKP uses it (concrete)</h3>
    <p>Every FastAPI endpoint's request body is a pydantic <code>BaseModel</code>. For example, in
       <code>vehicle-explore-service/app/main.py</code>:</p>
    <pre class="code">class SearchReq(BaseModel):
    query: str                       # required — missing it = automatic 422 error
    store: Optional[str] = None      # optional, defaults to None
    useLlm: bool = True              # default applied if absent
    topK: int = 5
    includeDiagram: bool = False
    origin: Optional[dict] = None</pre>
    <p>When the search portal POSTs JSON to <code>/api/vehicle-explore/{{ '{' }}framework{{ '}' }}/search</code>,
       FastAPI uses this model to:</p>
    <ul class="bullets">
      <li><b>validate + parse</b> the body before your handler runs (the handler only ever sees a clean, typed <code>SearchReq</code>),</li>
      <li>return an automatic <b>422 Unprocessable Entity</b> with a helpful message if, say, <code>query</code> is missing or <code>topK</code> isn't a number,</li>
      <li>apply <b>defaults</b> (<code>useLlm=True</code>, <code>topK=5</code>) so the handler doesn't deal with "what if it's not set?",</li>
      <li>and generate the <b>Swagger / OpenAPI docs</b> (<code>/docs</code>) from the model — that's where the request schema in the API docs comes from.</li>
    </ul>
    <p>Then the handler does <code>req.model_dump()</code> (e.g. <code>orchestrator.orchestrate(req.model_dump())</code>)
       to turn it back into a plain dict to pass downstream.</p>

    <p class="frame">
      <b>In short:</b> pydantic is the "front door" that turns untrusted JSON into validated, typed
      objects — so the rest of the Python service can trust its inputs, and the API documents itself.
      It's the same role that the <b>DTO + <code>&#64;Valid</code></b> request classes play on the
      Java/Spring side of VKP.
    </p>

    <h3>Where it's used in this codebase</h3>
    <table class="uses">
      <thead><tr><th>Service</th><th>File</th><th>Pydantic models (request bodies)</th></tr></thead>
      <tbody>
        <tr *ngFor="let u of usages">
          <td><b>{{ u.service }}</b></td><td><code>{{ u.file }}</code></td><td>{{ u.models }}</td>
        </tr>
      </tbody>
    </table>
    <p class="foot">All four Python (FastAPI) services use it for their endpoint request bodies. The
       Java/Spring services don't use pydantic — they use the equivalent <code>ReqDTO</code> + Jakarta
       <code>&#64;Valid</code> validation instead.</p>
  </div>
  `,
  styles: [`
    .tool { padding: 1rem 1.5rem; max-width: 1040px; }
    .tool h2 { margin: 0 0 .4rem; }
    .tool h3 { margin: 1.5rem 0 .5rem; color:#1f2933; }
    .tool .lead { font-size:.96rem; line-height:1.6; color:#344054; }
    .tool code { background:#f1f3f9; padding:.05rem .35rem; border-radius:4px; font-size:.85rem; }
    .tool .gives, .tool .bullets { line-height:1.7; color:#344054; font-size:.92rem; }
    .tool .code { background:#0c111d; color:#d1e0ff; padding:.9rem; border-radius:8px; font-size:.82rem; white-space:pre; overflow-x:auto; line-height:1.55; }
    .tool .frame { background:#f7f9ff; border:1px solid #e0e7ff; border-left:3px solid #3538cd; border-radius:6px; padding:.7rem .9rem; font-size:.9rem; line-height:1.6; color:#344054; }
    .uses { border-collapse:collapse; width:100%; font-size:.9rem; margin:.5rem 0 1rem; }
    .uses th, .uses td { border:1px solid #eaecf0; padding:.5rem .7rem; text-align:left; }
    .uses thead th { background:#f6f1ff; color:#4c1d95; }
    .uses tbody tr:hover { background:#faf8ff; }
    .tool .foot { color:#475467; font-size:.9rem; }
  `]
})
export class PydanticComponent {
  readonly usages = [
    { service: 'vehicle-explore-service', file: 'app/main.py', models: 'SearchReq, StageReq' },
    { service: 'agentic-service', file: 'app/main.py', models: 'RunReq' },
    { service: 'guardrails-service', file: 'app/models.py', models: 'InputCheckReq, OutputCheckReq, FeedbackReq' },
    { service: 'context-engine-service (CEF)', file: 'app/main.py', models: 'OrchestrateReq' },
  ];
}
