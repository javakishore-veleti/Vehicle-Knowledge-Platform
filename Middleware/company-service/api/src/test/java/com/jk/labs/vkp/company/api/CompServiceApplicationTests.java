package com.jk.labs.vkp.company.api;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** End-to-end CRUD smoke test against the default H2 profile. */
@SpringBootTest
@AutoConfigureMockMvc
class CompServiceApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void contextLoads() {
    }

    @Test
    void companyAndResourceCrudFlow() throws Exception {
        // create company
        String createResp = mockMvc.perform(post("/admin/company/service/v1/crud/companies")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Acme Motors\",\"description\":\"EV maker\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.company.companyId").exists())
                .andExpect(jsonPath("$.company.status").value("ACTIVE"))
                .andReturn().getResponse().getContentAsString();

        JsonNode node = objectMapper.readTree(createResp);
        String companyId = node.path("company").path("companyId").asText();

        // get company
        mockMvc.perform(get("/admin/company/service/v1/crud/companies/{id}", companyId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.company.name").value("Acme Motors"));

        // list companies
        mockMvc.perform(get("/admin/company/service/v1/crud/companies"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(1));

        // add a resource to the company
        mockMvc.perform(post("/admin/company/service/v1/crud/companies/{id}/resources", companyId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"resourceName\":\"Site\",\"resourceLink\":\"https://acme.example\",\"resourceType\":\"WEBSITE\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.resource.companyResourceId").exists())
                .andExpect(jsonPath("$.resource.companyId").value(companyId));

        // list resources
        mockMvc.perform(get("/admin/company/service/v1/crud/companies/{id}/resources", companyId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(1));

        // delete company
        mockMvc.perform(delete("/admin/company/service/v1/crud/companies/{id}", companyId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deleted").value(true));
    }

    @Test
    void getMissingCompanyReturns404() throws Exception {
        mockMvc.perform(get("/admin/company/service/v1/crud/companies/{id}", "does-not-exist"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }
}
