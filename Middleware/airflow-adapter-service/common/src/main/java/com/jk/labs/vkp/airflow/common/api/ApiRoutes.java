package com.jk.labs.vkp.airflow.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Versioned, internal API route prefixes. This service is service-to-service only
 * (no portal), so the audience is {@code internal}.
 *
 * Convention: {@code /<audience>/<domain>/service/v<major>/<resource>}.
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    public static final String API_BASE = "/internal/airflow/service/v1";

    /** A specific DAG's run collection: {@code .../dags/{dagId}/runs}. */
    public static final String DAG_RUNS = API_BASE + "/dags/{dagId}/runs";

    /** A specific DAG run: {@code .../dags/{dagId}/runs/{runId}}. */
    public static final String DAG_RUN = DAG_RUNS + "/{runId}";
}
