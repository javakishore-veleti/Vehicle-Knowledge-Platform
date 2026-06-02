package com.jk.labs.vkp.airflow.common.error;

/** Thrown when a DAG or DAG run does not exist in Airflow. Maps to HTTP 404. */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
