/** Wire models matching the VKP backend services. */

export interface Company {
  companyId?: string;
  name: string;
  description?: string;
  status?: string;
  createdDt?: string;
  updatedDt?: string;
}

export interface WorkflowRun {
  dagId: string;
  dagRunId: string;
  state: string;
  startDate?: string;
  endDate?: string;
}

export interface ResourceGraphNode {
  resourceGraphId: string;
  companyId: string;
  companyResourceId?: string;
  parentResourceGraphId?: string;
  resourceUrl: string;
  resourceType?: string;
  crawlStatus?: string;
  status?: string;
  createdDt?: string;
  updatedDt?: string;
}

export interface DiscoverResult {
  rootResourceGraphId: string;
  dagId: string;
  dagRunId: string;
  state: string;
}

/** Data Management section -> Airflow DAG id. */
export const SECTION_DAGS: Record<string, string> = {
  'data-collection': 'vkp_discover_resources',
  'data-ingestion': 'vkp_process_resources',
  'data-indexing': 'vkp_langgraph_index_content'
};

export const SECTION_LABELS: Record<string, string> = {
  'data-collection': 'Data Collection',
  'data-ingestion': 'Data Ingestion',
  'data-indexing': 'Data Indexing'
};
