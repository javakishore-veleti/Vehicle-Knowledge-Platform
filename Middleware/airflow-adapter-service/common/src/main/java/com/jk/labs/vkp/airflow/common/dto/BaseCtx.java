package com.jk.labs.vkp.airflow.common.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * Base context object for every use case. No method takes independent arguments: each
 * receives a single {@code <UseCase>Ctx} carrying both the request and response DTOs.
 */
@Getter
@Setter
public abstract class BaseCtx<Req, Resp> {

    private Req reqDTO;
    private Resp respDTO;
}
