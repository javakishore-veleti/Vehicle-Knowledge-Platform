package com.jk.labs.vkp.user.common.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * Base context object for every use case.
 *
 * Per the VKP architecture, no method takes independent arguments: every method
 * from controller to DAO receives a single {@code <UseCase>Ctx} which carries both
 * the request DTO and the response DTO. Concrete contexts extend this base and bind
 * the two type parameters, e.g.
 * {@code class CreateUserCtx extends BaseCtx<CreateUserReqDTO, CreateUserRespDTO>}.
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
