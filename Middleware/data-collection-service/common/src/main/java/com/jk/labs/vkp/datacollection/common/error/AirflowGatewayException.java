package com.jk.labs.vkp.datacollection.common.error;

/**
 * Thrown when the airflow-adapter-service is unreachable or returns an error. Maps to
 * HTTP 502 — this service is up but the downstream adapter call failed.
 */
public class AirflowGatewayException extends RuntimeException {

    public AirflowGatewayException(String message, Throwable cause) {
        super(message, cause);
    }

    public AirflowGatewayException(String message) {
        super(message);
    }
}
