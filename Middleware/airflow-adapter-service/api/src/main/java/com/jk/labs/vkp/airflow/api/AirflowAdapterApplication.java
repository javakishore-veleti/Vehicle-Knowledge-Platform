package com.jk.labs.vkp.airflow.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the VKP Airflow Adapter Service — the single gateway every service
 * uses to invoke Apache Airflow. Beans live across sibling modules (api / service), so the
 * component scan is widened to the service root package.
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.airflow")
public class AirflowAdapterApplication {

    public static void main(String[] args) {
        SpringApplication.run(AirflowAdapterApplication.class, args);
    }
}
