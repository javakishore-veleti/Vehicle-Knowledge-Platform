package com.jk.labs.vkp.airflow.service;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** Airflow connection settings, bound from {@code airflow.*}. */
@Component
@ConfigurationProperties(prefix = "airflow")
@Getter
@Setter
public class AirflowProperties {

    /** Base URL of the Airflow webserver REST API. */
    private String baseUrl = "http://localhost:8080";

    /** Basic-auth username for the Airflow REST API. */
    private String username = "admin";

    /** Basic-auth password for the Airflow REST API. */
    private String password = "admin";
}
