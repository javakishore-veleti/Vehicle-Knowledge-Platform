import { Routes } from '@angular/router';
import { CompaniesComponent } from './features/companies/companies.component';
import { WorkflowsComponent } from './features/data-management/workflows.component';
import { OverviewComponent } from './features/data-management/overview.component';
import { ResourceGraphComponent } from './features/data-management/resource-graph.component';

export const routes: Routes = [
  { path: '', redirectTo: 'companies', pathMatch: 'full' },

  { path: 'companies', component: CompaniesComponent, title: 'Companies' },

  { path: 'data-management', redirectTo: 'data-management/data-collection/workflows', pathMatch: 'full' },
  { path: 'data-management/data-collection/graph', component: ResourceGraphComponent, title: 'Resource Graph' },
  { path: 'data-management/:section/overview', component: OverviewComponent, title: 'Data Management' },
  { path: 'data-management/:section/workflows', component: WorkflowsComponent, title: 'Workflows' },
  { path: 'data-management/:section', redirectTo: 'data-management/:section/workflows', pathMatch: 'full' },

  { path: '**', redirectTo: 'companies' }
];
