package com.jk.labs.vkp.ingestion.service;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** Connection settings for airflow-adapter-service, bound from {@code airflow-adapter.*}. */
@Component
@ConfigurationProperties(prefix = "airflow-adapter")
@Getter
@Setter
public class AirflowAdapterProperties {

    /** Base URL of airflow-adapter-service (the only component that talks to Airflow). */
    private String baseUrl = "http://localhost:8083";
}
