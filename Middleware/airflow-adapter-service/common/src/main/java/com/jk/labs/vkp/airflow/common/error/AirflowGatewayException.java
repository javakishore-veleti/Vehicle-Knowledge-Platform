package com.jk.labs.vkp.airflow.common.error;

/**
 * Thrown when Airflow is unreachable or returns an unexpected error. Maps to HTTP 502
 * (Bad Gateway) — the adapter is up but the upstream Airflow call failed.
 */
public class AirflowGatewayException extends RuntimeException {

    public AirflowGatewayException(String message, Throwable cause) {
        super(message, cause);
    }

    public AirflowGatewayException(String message) {
        super(message);
    }
}
