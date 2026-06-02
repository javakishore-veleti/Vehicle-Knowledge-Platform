package com.jk.labs.vkp.user.api.controller;

import com.jk.labs.vkp.user.common.api.ApiRoutes;
import com.jk.labs.vkp.user.common.dto.profile.GetProfileCtx;
import com.jk.labs.vkp.user.common.dto.profile.GetProfileReqDTO;
import com.jk.labs.vkp.user.common.dto.profile.GetProfileRespDTO;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileCtx;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileReqDTO;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileRespDTO;
import com.jk.labs.vkp.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Profile endpoints. The user is currently addressed by id in the path; resolving the
 * "current user" from the bearer JWT is a follow-up once a security filter is added.
 */
@RestController
@RequestMapping(ApiRoutes.PROFILE)
@RequiredArgsConstructor
public class ProfileController {

    private final UserService userService;

    @GetMapping("/{userId}")
    public GetProfileRespDTO get(@PathVariable String userId) {
        GetProfileCtx ctx = new GetProfileCtx();
        ctx.setReqDTO(new GetProfileReqDTO(userId));
        userService.getProfile(ctx);
        return ctx.getRespDTO();
    }

    @PutMapping("/{userId}")
    public UpdateProfileRespDTO update(@PathVariable String userId,
                                       @Valid @RequestBody UpdateProfileReqDTO req) {
        req.setUserId(userId);
        UpdateProfileCtx ctx = new UpdateProfileCtx();
        ctx.setReqDTO(req);
        userService.updateProfile(ctx);
        return ctx.getRespDTO();
    }
}
