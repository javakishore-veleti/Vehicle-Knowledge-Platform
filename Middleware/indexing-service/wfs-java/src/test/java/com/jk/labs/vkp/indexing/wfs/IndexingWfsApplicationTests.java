package com.jk.labs.vkp.indexing.wfs;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Verifies wiring without external infra: lazy-init avoids eagerly creating the ONNX embedding
 * model (a model download) and the pgVector datasource is excluded (no DB needed at test time).
 */
@SpringBootTest(properties = {
        "spring.main.lazy-initialization=true",
        "spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration"
})
class IndexingWfsApplicationTests {

    @Test
    void contextLoads() {
    }
}
