import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterLink, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';
import { PanelMenuModule } from 'primeng/panelmenu';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, PanelMenuModule],
  template: `
  <div class="vkp-shell">
    <!-- Top bar -->
    <header class="vkp-topbar">
      <div class="vkp-brand"><i class="pi pi-car"></i> VKP Admin</div>
      <nav class="vkp-mainnav">
        <a routerLink="/companies" [class.active]="mainMenu() === 'companies'">
          <i class="pi pi-building"></i> Companies
        </a>
        <a routerLink="/data-management" [class.active]="mainMenu() === 'data-management'">
          <i class="pi pi-sitemap"></i> Data Management
        </a>
        <a routerLink="/agents" [class.active]="mainMenu() === 'agents'">
          <i class="pi pi-android"></i> AI Agents
        </a>
      </nav>
      <div class="vkp-topbar-right">
        <i class="pi pi-search" title="Search"></i>
        <i class="pi pi-cog" title="Settings"></i>
        <span class="vkp-user"><span class="vkp-avatar">AD</span> Admin</span>
      </div>
    </header>

    <!-- Body: contextual sidebar + content -->
    <div class="vkp-body">
      <aside class="vkp-sidebar">
        <div class="vkp-sidebar-title">{{ sidebarTitle() }}</div>
        <p-panelMenu [model]="sideMenu()" [multiple]="true"></p-panelMenu>
      </aside>
      <main class="vkp-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  </div>
  `
})
export class AppComponent {
  readonly url = signal<string>('/');

  readonly mainMenu = computed(() => {
    const u = this.url();
    if (u.startsWith('/data-management')) { return 'data-management'; }
    if (u.startsWith('/agents')) { return 'agents'; }
    return 'companies';
  });

  private readonly companiesMenu: MenuItem[] = [
    { label: 'Companies', icon: 'pi pi-building', routerLink: '/companies' },
    { label: 'Resources', icon: 'pi pi-link', routerLink: '/companies/resources' },
    { label: 'Resource Graph', icon: 'pi pi-sitemap', routerLink: '/companies/graph' }
  ];

  private readonly dataMenu: MenuItem[] = [
    {
      label: 'Data Collection', icon: 'pi pi-compass', expanded: true,
      items: [
        { label: 'Overview', icon: 'pi pi-info-circle', routerLink: '/data-management/data-collection/overview' },
        { label: 'Crawl Snapshot', icon: 'pi pi-cloud-download', routerLink: '/data-management/data-collection/crawl' },
        { label: 'Snapshot Browser', icon: 'pi pi-images', routerLink: '/data-management/data-collection/snapshots' },
        { label: 'Workflows', icon: 'pi pi-bolt', routerLink: '/data-management/data-collection/workflows' },
        { label: 'Resource Graph', icon: 'pi pi-sitemap', routerLink: '/data-management/data-collection/graph' }
      ]
    },
    {
      label: 'Data Ingestion', icon: 'pi pi-download',
      items: [
        { label: 'Overview', icon: 'pi pi-info-circle', routerLink: '/data-management/data-ingestion/overview' },
        { label: 'Workflows', icon: 'pi pi-bolt', routerLink: '/data-management/data-ingestion/workflows' }
      ]
    },
    {
      label: 'Data Indexing', icon: 'pi pi-database',
      items: [
        { label: 'Overview', icon: 'pi pi-info-circle', routerLink: '/data-management/data-indexing/overview' },
        { label: 'Trigger Indexing', icon: 'pi pi-bolt', routerLink: '/data-management/data-indexing/trigger' },
        { label: 'Workflows', icon: 'pi pi-sitemap', routerLink: '/data-management/data-indexing/workflows' },
        { label: 'Index Formulas', icon: 'pi pi-sliders-h', routerLink: '/data-management/data-indexing/formulas' },
        { label: 'Provider Credentials', icon: 'pi pi-key', routerLink: '/data-management/data-indexing/credentials' },
        { label: 'Index Logs', icon: 'pi pi-list', routerLink: '/data-management/data-indexing/logs' }
      ]
    },
    {
      label: 'Guardrails', icon: 'pi pi-shield',
      items: [
        { label: 'Query Log', icon: 'pi pi-list', routerLink: '/data-management/guardrails/queries' }
      ]
    }
  ];

  private readonly agentsMenu: MenuItem[] = [
    {
      label: 'Agent Roster', icon: 'pi pi-android', expanded: true,
      items: [
        { label: 'Roster & Run', icon: 'pi pi-table', routerLink: '/agents/roster' }
      ]
    }
  ];

  readonly sideMenu = computed(() => {
    switch (this.mainMenu()) {
      case 'data-management': return this.dataMenu;
      case 'agents': return this.agentsMenu;
      default: return this.companiesMenu;
    }
  });

  readonly sidebarTitle = computed(() => {
    switch (this.mainMenu()) {
      case 'data-management': return 'Data Management';
      case 'agents': return 'AI Agents';
      default: return 'Companies';
    }
  });

  constructor(router: Router) {
    this.url.set(router.url);
    router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(e => this.url.set(e.urlAfterRedirects));
  }
}
