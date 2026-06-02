package com.jk.labs.vkp.ingestion.api;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/** Verifies the application context wires up on H2 (no adapter/Airflow needed at startup). */
@SpringBootTest
class IngestionApplicationTests {

    @Test
    void contextLoads() {
    }
}
