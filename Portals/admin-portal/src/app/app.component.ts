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
        <div class="vkp-sidebar-title">{{ mainMenu() === 'companies' ? 'Companies' : 'Data Management' }}</div>
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

  readonly mainMenu = computed(() => (this.url().startsWith('/data-management') ? 'data-management' : 'companies'));

  private readonly companiesMenu: MenuItem[] = [
    { label: 'Companies', icon: 'pi pi-building', routerLink: '/companies' },
    { label: 'Resources', icon: 'pi pi-link', disabled: true }
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
    }
  ];

  readonly sideMenu = computed(() => (this.mainMenu() === 'data-management' ? this.dataMenu : this.companiesMenu));

  constructor(router: Router) {
    this.url.set(router.url);
    router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(e => this.url.set(e.urlAfterRedirects));
  }
}
