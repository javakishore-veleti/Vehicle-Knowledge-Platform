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
