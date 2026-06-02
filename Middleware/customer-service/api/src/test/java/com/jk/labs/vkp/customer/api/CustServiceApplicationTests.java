package com.jk.labs.vkp.customer.api;

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
class CustServiceApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void contextLoads() {
    }

    @Test
    void customerAndResourceCrudFlow() throws Exception {
        // create customer
        String createResp = mockMvc.perform(post("/admin/customer/service/v1/crud/customers")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Acme Motors\",\"description\":\"EV maker\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.customer.customerId").exists())
                .andExpect(jsonPath("$.customer.status").value("ACTIVE"))
                .andReturn().getResponse().getContentAsString();

        JsonNode node = objectMapper.readTree(createResp);
        String customerId = node.path("customer").path("customerId").asText();

        // get customer
        mockMvc.perform(get("/admin/customer/service/v1/crud/customers/{id}", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customer.name").value("Acme Motors"));

        // list customers
        mockMvc.perform(get("/admin/customer/service/v1/crud/customers"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(1));

        // add a resource to the customer
        mockMvc.perform(post("/admin/customer/service/v1/crud/customers/{id}/resources", customerId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"resourceName\":\"Site\",\"resourceLink\":\"https://acme.example\",\"resourceType\":\"WEBSITE\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.resource.customerResourceId").exists())
                .andExpect(jsonPath("$.resource.customerId").value(customerId));

        // list resources
        mockMvc.perform(get("/admin/customer/service/v1/crud/customers/{id}/resources", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(1));

        // delete customer
        mockMvc.perform(delete("/admin/customer/service/v1/crud/customers/{id}", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deleted").value(true));
    }

    @Test
    void getMissingCustomerReturns404() throws Exception {
        mockMvc.perform(get("/admin/customer/service/v1/crud/customers/{id}", "does-not-exist"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }
}
