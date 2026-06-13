import { Routes } from '@angular/router';
import { CompaniesComponent } from './features/companies/companies.component';
import { ResourcesComponent } from './features/companies/resources.component';
import { CompanyGraphComponent } from './features/companies/company-graph.component';
import { WorkflowsComponent } from './features/data-management/workflows.component';
import { OverviewComponent } from './features/data-management/overview.component';
import { ResourceGraphComponent } from './features/data-management/resource-graph.component';
import { CrawlComponent } from './features/data-management/crawl.component';
import { SnapshotsComponent } from './features/data-management/snapshots.component';
import { IndexOverviewComponent } from './features/data-management/indexing/index-overview.component';
import { TriggerIndexComponent } from './features/data-management/indexing/trigger-index.component';
import { IndexWorkflowsComponent } from './features/data-management/indexing/index-workflows.component';
import { IndexFormulasComponent } from './features/data-management/indexing/index-formulas.component';
import { IndexCredentialsComponent } from './features/data-management/indexing/index-credentials.component';
import { IndexLogsComponent } from './features/data-management/indexing/index-logs.component';
import { QueryLogComponent } from './features/data-management/guardrails/query-log.component';
import { AgentRosterComponent } from './features/agents/roster.component';
import { AgenticPatternsComponent } from './features/resources/agentic-patterns.component';
import { PydanticComponent } from './features/resources/pydantic.component';
import { DmPipelinesComponent } from './features/resources/dm-pipelines.component';
import { InteractiveLabComponent } from './features/resources/interactive-lab.component';
import { CollectionVsIngestionComponent } from './features/resources/collection-vs-ingestion.component';
import { DbModelComponent } from './features/resources/db-model.component';
import { MasteryMapComponent } from './features/resources/mastery-map.component';
import { FrameworkPatternsComponent } from './features/resources/framework-patterns.component';
import { AgentPatternsOverviewComponent } from './features/resources/agent-patterns-overview.component';

export const routes: Routes = [
  { path: '', redirectTo: 'companies', pathMatch: 'full' },

  { path: 'resources', redirectTo: 'resources/mastery/map', pathMatch: 'full' },
  { path: 'resources/mastery', redirectTo: 'resources/mastery/map', pathMatch: 'full' },
  { path: 'resources/mastery/map', component: MasteryMapComponent, title: 'Mastery Map' },
  { path: 'resources/design-patterns', redirectTo: 'resources/design-patterns/agentic-patterns', pathMatch: 'full' },
  { path: 'resources/design-patterns/overview', component: AgentPatternsOverviewComponent, title: 'Agent Patterns Overview' },
  { path: 'resources/design-patterns/agentic-patterns', component: AgenticPatternsComponent, title: 'Agentic Patterns' },
  { path: 'resources/design-patterns/langgraph', component: FrameworkPatternsComponent, data: { fw: 'langgraph' }, title: 'LangGraph Patterns' },
  { path: 'resources/design-patterns/crewai', component: FrameworkPatternsComponent, data: { fw: 'crewai' }, title: 'CrewAI Patterns' },
  { path: 'resources/tools', redirectTo: 'resources/tools/pydantic', pathMatch: 'full' },
  { path: 'resources/tools/pydantic', component: PydanticComponent, title: 'Pydantic' },
  { path: 'resources/architecture', redirectTo: 'resources/architecture/data-management/pipelines', pathMatch: 'full' },
  { path: 'resources/architecture/data-management/pipelines', component: DmPipelinesComponent, title: 'Data Management Pipelines' },
  { path: 'resources/architecture/data-management/interactive-lab', component: InteractiveLabComponent, title: 'Interactive Lab' },
  { path: 'resources/architecture/data-management/collection-vs-ingestion', component: CollectionVsIngestionComponent, title: 'Collection vs Ingestion' },
  { path: 'resources/architecture/data-management/database-model', component: DbModelComponent, title: 'Database Model' },

  { path: 'companies', component: CompaniesComponent, title: 'Companies' },
  { path: 'companies/resources', component: ResourcesComponent, title: 'Company Resources' },
  { path: 'companies/graph', component: CompanyGraphComponent, title: 'Resource Graph' },

  { path: 'agents', redirectTo: 'agents/roster', pathMatch: 'full' },
  { path: 'agents/roster', component: AgentRosterComponent, title: 'Agent Roster' },

  { path: 'data-management', redirectTo: 'data-management/data-collection/workflows', pathMatch: 'full' },
  { path: 'data-management/data-collection/crawl', component: CrawlComponent, title: 'Crawl Snapshot' },
  { path: 'data-management/data-collection/snapshots', component: SnapshotsComponent, title: 'Snapshot Browser' },
  { path: 'data-management/data-collection/graph', component: ResourceGraphComponent, title: 'Resource Graph' },

  // Data Indexing — dedicated pages (must precede the generic :section routes)
  { path: 'data-management/data-indexing/overview', component: IndexOverviewComponent, title: 'Indexing Overview' },
  { path: 'data-management/data-indexing/trigger', component: TriggerIndexComponent, title: 'Trigger Indexing' },
  { path: 'data-management/data-indexing/workflows', component: IndexWorkflowsComponent, title: 'Indexing Workflows' },
  { path: 'data-management/data-indexing/formulas', component: IndexFormulasComponent, title: 'Index Formulas' },
  { path: 'data-management/data-indexing/credentials', component: IndexCredentialsComponent, title: 'Provider Credentials' },
  { path: 'data-management/data-indexing/logs', component: IndexLogsComponent, title: 'Index Logs' },

  { path: 'data-management/guardrails/queries', component: QueryLogComponent, title: 'Guardrails Query Log' },

  { path: 'data-management/:section/overview', component: OverviewComponent, title: 'Data Management' },
  { path: 'data-management/:section/workflows', component: WorkflowsComponent, title: 'Workflows' },
  { path: 'data-management/:section', redirectTo: 'data-management/:section/workflows', pathMatch: 'full' },

  { path: '**', redirectTo: 'companies' }
];
