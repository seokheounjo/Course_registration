package com.example.course_registration.security;

import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import com.example.course_registration.service.LoginService;

import java.util.Collections;

@Component
public class CustomAuthenticationProvider implements AuthenticationProvider {

    private final LoginService loginService;

    public CustomAuthenticationProvider(LoginService loginService) {
        this.loginService = loginService;
    }

    @Override
    public Authentication authenticate(Authentication authentication)
            throws AuthenticationException {

        String userId   = authentication.getName();
        String password = authentication.getCredentials().toString();

        String role = loginService
                .authenticate(userId, password)
                .orElseThrow(() -> new BadCredentialsException("잘못된 로그인 정보입니다."));

        return new UsernamePasswordAuthenticationToken(
                userId,
                password,
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role))
        );
    }

    @Override
    public boolean supports(Class<?> authentication) {
        return UsernamePasswordAuthenticationToken.class
                .isAssignableFrom(authentication);
    }
}
