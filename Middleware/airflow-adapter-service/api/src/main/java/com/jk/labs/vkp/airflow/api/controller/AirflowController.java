package com.jk.labs.vkp.airflow.api.controller;

import com.jk.labs.vkp.airflow.common.api.ApiRoutes;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunCtx;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunCtx;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.list.ListRunsCtx;
import com.jk.labs.vkp.airflow.common.dto.list.ListRunsReqDTO;
import com.jk.labs.vkp.airflow.common.dto.list.ListRunsRespDTO;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunCtx;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksCtx;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksReqDTO;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksRespDTO;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagCtx;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagReqDTO;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagRespDTO;
import com.jk.labs.vkp.airflow.service.AirflowService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * The single REST surface other services call to operate Airflow. Controllers adapt HTTP
 * to the use case {@code Ctx} and never touch Airflow directly.
 */
@RestController
@RequiredArgsConstructor
public class AirflowController {

    private final AirflowService airflowService;

    @PostMapping(ApiRoutes.DAG_RUNS)
    @ResponseStatus(HttpStatus.CREATED)
    public TriggerDagRespDTO trigger(@PathVariable String dagId,
                                     @RequestBody(required = false) TriggerDagReqDTO body) {
        TriggerDagReqDTO req = body != null ? body : new TriggerDagReqDTO();
        req.setDagId(dagId);
        TriggerDagCtx ctx = new TriggerDagCtx();
        ctx.setReqDTO(req);
        airflowService.trigger(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.DAG_RUNS)
    public ListRunsRespDTO listRuns(@PathVariable String dagId,
                                    @RequestParam(defaultValue = "25") int limit) {
        ListRunsCtx ctx = new ListRunsCtx();
        ctx.setReqDTO(new ListRunsReqDTO(dagId, limit));
        airflowService.listRuns(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.DAG_RUN)
    public GetRunRespDTO getRun(@PathVariable String dagId, @PathVariable String runId) {
        GetRunCtx ctx = new GetRunCtx();
        ctx.setReqDTO(new GetRunReqDTO(dagId, runId));
        airflowService.getRun(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.DAG_RUN + "/tasks")
    public GetTasksRespDTO getTasks(@PathVariable String dagId, @PathVariable String runId) {
        GetTasksCtx ctx = new GetTasksCtx();
        ctx.setReqDTO(new GetTasksReqDTO(dagId, runId));
        airflowService.getTasks(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.DAG_RUN + "/retry")
    public RetryRunRespDTO retry(@PathVariable String dagId, @PathVariable String runId) {
        RetryRunCtx ctx = new RetryRunCtx();
        ctx.setReqDTO(new RetryRunReqDTO(dagId, runId));
        airflowService.retry(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.DAG_RUN + "/cancel")
    public CancelRunRespDTO cancel(@PathVariable String dagId, @PathVariable String runId) {
        CancelRunCtx ctx = new CancelRunCtx();
        ctx.setReqDTO(new CancelRunReqDTO(dagId, runId));
        airflowService.cancel(ctx);
        return ctx.getRespDTO();
    }
}
