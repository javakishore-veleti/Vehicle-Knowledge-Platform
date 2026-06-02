# VKP Admin Portal

Angular 19 + PrimeNG admin portal for the Vehicle Knowledge Platform. Light, professional
theme with a fixed top bar and a contextual left sidebar.

## Navigation
- **Companies** (top-nav main menu) → Companies CRUD + search (→ `company-service`).
- **Data Management** (top-nav main menu) → left nav for **Data Collection / Data Ingestion /
  Data Indexing**, each with **Overview** and **Workflows** (Airflow DAG runs via
  `data-collection-service` → `airflow-adapter-service`).

## Run (dev)
From the repo root:
```bash
npm run localhost:portals:admin:install   # first time only
npm run localhost:containers:start-all     # MongoDB / Postgres / Airflow
npm run localhost:services:java:start-all  # company / adapter / data-collection / …
npm run localhost:portals:admin:start      # ng serve on http://localhost:4200
```
Or directly: `cd Portals/admin-portal && npm start`.

The dev server proxies API calls to the backends (see `proxy.conf.json`):
- `/admin/company/**` → `http://localhost:8081` (company-service)
- `/admin/data-collection/**` → `http://localhost:8084` (data-collection-service)

So no CORS config is needed on the services in local dev.

## Structure
- `src/app/app.component.ts` — shell (top bar + contextual sidebar via PrimeNG PanelMenu)
- `src/app/core/` — models + HTTP services (`CompanyService`, `WorkflowService`)
- `src/app/features/companies/` — Companies CRUD (PrimeNG table + dialog)
- `src/app/features/data-management/` — Overview + Workflows pages
