package com.jk.labs.vkp.user.api.controller;

import com.jk.labs.vkp.user.common.api.ApiRoutes;
import com.jk.labs.vkp.user.common.dto.auth.ForgotPasswordCtx;
import com.jk.labs.vkp.user.common.dto.auth.ForgotPasswordReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.ForgotPasswordRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordCtx;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.SigninCtx;
import com.jk.labs.vkp.user.common.dto.auth.SigninReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.SigninRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.SignupCtx;
import com.jk.labs.vkp.user.common.dto.auth.SignupReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.SignupRespDTO;
import com.jk.labs.vkp.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** Authentication endpoints: signup, signin, password reset. */
@RestController
@RequestMapping(ApiRoutes.AUTH)
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;

    @PostMapping("/signup")
    @ResponseStatus(HttpStatus.CREATED)
    public SignupRespDTO signup(@Valid @RequestBody SignupReqDTO req) {
        SignupCtx ctx = new SignupCtx();
        ctx.setReqDTO(req);
        userService.signup(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping("/signin")
    public SigninRespDTO signin(@Valid @RequestBody SigninReqDTO req) {
        SigninCtx ctx = new SigninCtx();
        ctx.setReqDTO(req);
        userService.signin(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping("/forgot-password")
    public ForgotPasswordRespDTO forgotPassword(@Valid @RequestBody ForgotPasswordReqDTO req) {
        ForgotPasswordCtx ctx = new ForgotPasswordCtx();
        ctx.setReqDTO(req);
        userService.forgotPassword(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping("/reset-password")
    public ResetPasswordRespDTO resetPassword(@Valid @RequestBody ResetPasswordReqDTO req) {
        ResetPasswordCtx ctx = new ResetPasswordCtx();
        ctx.setReqDTO(req);
        userService.resetPassword(ctx);
        return ctx.getRespDTO();
    }
}
