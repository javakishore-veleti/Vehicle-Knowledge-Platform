package com.jk.labs.vkp.airflow.service;

import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import com.jk.labs.vkp.airflow.common.dto.TaskInstanceDTO;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunCtx;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.cancel.CancelRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunCtx;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.retry.RetryRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunCtx;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunReqDTO;
import com.jk.labs.vkp.airflow.common.dto.run.GetRunRespDTO;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksCtx;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksReqDTO;
import com.jk.labs.vkp.airflow.common.dto.tasks.GetTasksRespDTO;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagCtx;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagReqDTO;
import com.jk.labs.vkp.airflow.common.dto.trigger.TriggerDagRespDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Normalizes Airflow DAG operations behind the adapter's clean API. Every method takes
 * only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class AirflowService {

    private static final String CANCELLED_STATE = "failed";

    private final AirflowClient client;

    public void trigger(TriggerDagCtx ctx) {
        TriggerDagReqDTO req = ctx.getReqDTO();
        DagRunDTO run = client.triggerDagRun(req.getDagId(), req.getConf(), req.getNote());
        log.info("Triggered DAG {} -> run {} (by {})", req.getDagId(), run.getDagRunId(), req.getTriggeredBy());
        ctx.setRespDTO(new TriggerDagRespDTO(run));
    }

    public void getRun(GetRunCtx ctx) {
        GetRunReqDTO req = ctx.getReqDTO();
        DagRunDTO run = client.getDagRun(req.getDagId(), req.getRunId());
        ctx.setRespDTO(new GetRunRespDTO(run));
    }

    public void getTasks(GetTasksCtx ctx) {
        GetTasksReqDTO req = ctx.getReqDTO();
        List<TaskInstanceDTO> tasks = client.getTaskInstances(req.getDagId(), req.getRunId());
        ctx.setRespDTO(new GetTasksRespDTO(tasks, tasks.size()));
    }

    public void retry(RetryRunCtx ctx) {
        RetryRunReqDTO req = ctx.getReqDTO();
        DagRunDTO run = client.clearDagRun(req.getDagId(), req.getRunId());
        log.info("Retried (cleared) DAG run {}/{}", req.getDagId(), req.getRunId());
        ctx.setRespDTO(new RetryRunRespDTO(run));
    }

    public void cancel(CancelRunCtx ctx) {
        CancelRunReqDTO req = ctx.getReqDTO();
        DagRunDTO run = client.setDagRunState(req.getDagId(), req.getRunId(), CANCELLED_STATE);
        log.info("Cancelled DAG run {}/{}", req.getDagId(), req.getRunId());
        ctx.setRespDTO(new CancelRunRespDTO(run));
    }
}
