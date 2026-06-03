package com.jk.labs.vkp.indexing.wfs;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** Abstract executor API: control plane calls POST /wfs/{executorId}/execute. */
@RestController
@RequiredArgsConstructor
public class ExecuteController {

    private final SpringAiExecutor executor;

    @Data
    public static class ExecuteReq {
        @NotBlank
        private String indexLogId;
        private Map<String, Object> runtimeParams;
    }

    @Data
    public static class ExecuteResp {
        private final String indexLogId;
        private final boolean accepted;
    }

    @PostMapping("/wfs/{executorId}/execute")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public ExecuteResp execute(@PathVariable String executorId, @RequestBody ExecuteReq req) {
        executor.execute(executorId, req.getIndexLogId(),
                req.getRuntimeParams() == null ? Map.of() : req.getRuntimeParams());
        return new ExecuteResp(req.getIndexLogId(), true);
    }
}
