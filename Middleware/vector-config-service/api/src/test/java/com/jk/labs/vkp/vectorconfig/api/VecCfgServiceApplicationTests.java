package com.jk.labs.vkp.vectorconfig.api;

import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.VecCfgDTO;
import com.jk.labs.vkp.vectorconfig.common.error.InvalidConfigException;
import com.jk.labs.vkp.vectorconfig.service.VecCfgService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
class VecCfgServiceApplicationTests {

    @Autowired
    private VecCfgService service;

    @Test
    void contextLoadsAndSeedDataPresent() {
        ListVecCfgsCtx ctx = new ListVecCfgsCtx();
        ctx.setReqDTO(new ListVecCfgsReqDTO("20000000-0000-4000-8000-000000000001", null, null));
        service.list(ctx);
        assertEquals(2, ctx.getRespDTO().getCount(),
                "Chevrolet resource should have 2 seeded configs (pgvector primary + mongo)");
    }

    @Test
    void createDemotesPreviousPrimary() {
        String resourceId = "20000000-0000-4000-8000-000000000001";
        // Add a new primary -> the seeded pgvector primary must be demoted.
        CreateVecCfgCtx create = new CreateVecCfgCtx();
        create.setReqDTO(new CreateVecCfgReqDTO(resourceId, VecCfgDTO.builder()
                .companyId("10000000-0000-4000-8000-000000000001")
                .vectorStoreType("weaviate")
                .isPrimary(true)
                .build()));
        service.create(create);

        ListVecCfgsCtx list = new ListVecCfgsCtx();
        list.setReqDTO(new ListVecCfgsReqDTO(resourceId, null, null));
        service.list(list);
        long primaries = list.getRespDTO().getVectorConfigs().stream()
                .filter(c -> Boolean.TRUE.equals(c.getIsPrimary())).count();
        assertEquals(1, primaries, "at most one primary per resource");
        assertTrue(list.getRespDTO().getVectorConfigs().stream()
                .anyMatch(c -> "weaviate".equals(c.getVectorStoreType()) && Boolean.TRUE.equals(c.getIsPrimary())));
    }

    @Test
    void rejectsUnsupportedStoreType() {
        CreateVecCfgCtx create = new CreateVecCfgCtx();
        create.setReqDTO(new CreateVecCfgReqDTO("20000000-0000-4000-8000-000000000002", VecCfgDTO.builder()
                .companyId("10000000-0000-4000-8000-000000000002")
                .vectorStoreType("faiss")
                .build()));
        assertThrows(InvalidConfigException.class, () -> service.create(create));
    }
}
