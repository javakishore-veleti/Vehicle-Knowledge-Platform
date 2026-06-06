package com.jk.labs.vkp.vectorconfig.common.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * Base context object for every use case.
 *
 * Per the VKP architecture, no method takes independent arguments: every method from
 * controller to DAO receives a single {@code <UseCase>Ctx} carrying both the request and
 * response DTOs. Concrete contexts bind the two type parameters.
 *
 * @param <Req>  the use case request DTO type
 * @param <Resp> the use case response DTO type
 */
@Getter
@Setter
public abstract class BaseCtx<Req, Resp> {

    private Req reqDTO;
    private Resp respDTO;
}
