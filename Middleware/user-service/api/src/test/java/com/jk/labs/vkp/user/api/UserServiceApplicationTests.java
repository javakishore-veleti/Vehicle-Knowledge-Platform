package com.jk.labs.vkp.user.api;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import org.springframework.test.context.TestPropertySource;

/** End-to-end auth + profile smoke test against the default H2 profile. */
@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = "vkp.jwt.enabled=false")
class UserServiceApplicationTests {

    private static final String AUTH = "/customer/user/service/v1/auth";
    private static final String PROFILE = "/customer/user/service/v1/profile";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void contextLoads() {
    }

    @Test
    void signupSigninProfileAndPasswordResetFlow() throws Exception {
        // signup
        String signupResp = mockMvc.perform(post(AUTH + "/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"Jane@Example.com\",\"password\":\"secret123\",\"firstName\":\"Jane\",\"lastName\":\"Doe\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.user.userId").exists())
                .andExpect(jsonPath("$.user.email").value("jane@example.com"))
                .andExpect(jsonPath("$.user.role").value("USER"))
                .andExpect(jsonPath("$.user.status").value("ACTIVE"))
                .andExpect(jsonPath("$.user.password").doesNotExist())
                .andReturn().getResponse().getContentAsString();
        String userId = objectMapper.readTree(signupResp).path("user").path("userId").asText();

        // duplicate email -> 409
        mockMvc.perform(post(AUTH + "/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"jane@example.com\",\"password\":\"secret123\",\"firstName\":\"Jane\"}"))
                .andExpect(status().isConflict());

        // signin OK -> token
        mockMvc.perform(post(AUTH + "/signin")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"jane@example.com\",\"password\":\"secret123\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists())
                .andExpect(jsonPath("$.tokenType").value("Bearer"));

        // signin wrong password -> 401
        mockMvc.perform(post(AUTH + "/signin")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"jane@example.com\",\"password\":\"wrong\"}"))
                .andExpect(status().isUnauthorized());

        // get profile
        mockMvc.perform(get(PROFILE + "/{id}", userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.user.firstName").value("Jane"));

        // update profile
        mockMvc.perform(put(PROFILE + "/{id}", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"Janet\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.user.firstName").value("Janet"));

        // forgot password -> reset token
        String forgotResp = mockMvc.perform(post(AUTH + "/forgot-password")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"jane@example.com\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.resetToken").exists())
                .andReturn().getResponse().getContentAsString();
        String resetToken = objectMapper.readTree(forgotResp).path("resetToken").asText();

        // reset password
        mockMvc.perform(post(AUTH + "/reset-password")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"resetToken\":\"" + resetToken + "\",\"newPassword\":\"newsecret123\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        // signin with new password
        mockMvc.perform(post(AUTH + "/signin")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"jane@example.com\",\"password\":\"newsecret123\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists());
    }
}
