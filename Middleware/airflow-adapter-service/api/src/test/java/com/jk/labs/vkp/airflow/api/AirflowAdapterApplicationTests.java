package com.jk.labs.vkp.airflow.api;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

/** Verifies the application context wires up (no Airflow connection needed at startup). */
@SpringBootTest
@TestPropertySource(properties = "vkp.jwt.enabled=false")
class AirflowAdapterApplicationTests {

    @Test
    void contextLoads() {
    }
}
