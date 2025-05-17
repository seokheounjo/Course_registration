package com.example.Course_registration.security;

import com.example.Course_registration.entity.Admin;
//import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Student;
import com.example.Course_registration.service.LoginService;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

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

        Object user = loginService
                .authenticate(userId, password)
                .orElseThrow(() -> new BadCredentialsException("잘못된 로그인 정보입니다."));

        String role;
        List<SimpleGrantedAuthority> authorities;

        if (user instanceof Student student) {
            role = "STUDENT";
            authorities = Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role));
            return new UsernamePasswordAuthenticationToken(student, null, authorities);

        } else if (user instanceof Admin admin) {
            role = "ADMIN";
            authorities = Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role));
            return new UsernamePasswordAuthenticationToken(admin, null, authorities);
        }
//        } else if (user instanceof Professor professor) {
//            role = "PROFESSOR";
//            authorities = Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role));
//            return new UsernamePasswordAuthenticationToken(professor, null, authorities);
//        }

        throw new BadCredentialsException("지원하지 않는 사용자 유형입니다.");
    }

    @Override
    public boolean supports(Class<?> authentication) {
        return UsernamePasswordAuthenticationToken.class.isAssignableFrom(authentication);
    }
}