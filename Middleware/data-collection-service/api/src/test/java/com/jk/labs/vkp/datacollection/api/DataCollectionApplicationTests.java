package com.jk.labs.vkp.datacollection.api;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

/** Verifies the application context wires up on H2 (no adapter/Airflow needed at startup). */
@SpringBootTest
@TestPropertySource(properties = "vkp.jwt.enabled=false")
class DataCollectionApplicationTests {

    @Test
    void contextLoads() {
    }
}
