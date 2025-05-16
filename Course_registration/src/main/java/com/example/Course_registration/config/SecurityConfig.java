package com.example.Course_registration.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // CSRF 비활성화 (필요에 따라 조정)
                .csrf().disable()

                // 정적 리소스와 /login 페이지는 모두 허용
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(
                                "/",
                                "/login",
                                "/css/**",
                                "/js/**",
                                "/images/**"    // ← images 폴더 추가
                        ).permitAll()
                        // 관리자·학생 역할별 접근 제어
                        .requestMatchers("/admin/**").hasRole("ADMIN")
                        .requestMatchers("/student/**").hasRole("STUDENT")
                        .anyRequest().authenticated()
                )

                // 로그인 설정
                .formLogin(login -> login
                        .loginPage("/login")                // 커스텀 로그인 페이지
                        .loginProcessingUrl("/login")       // 폼 action 과 일치시킴
                        .usernameParameter("studentId")     // name="studentId" 필드 사용
                        .passwordParameter("password")      // name="password" 필드 사용
                        .defaultSuccessUrl("/route", true)  // 로그인 성공 후 /route 로 이동
                        .permitAll()
                )

                // 로그아웃 설정
                .logout(logout -> logout
                        .logoutSuccessUrl("/login?logout")  // 로그아웃 성공 후
                        .permitAll()
                );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        // BCrypt 를 사용해 비밀번호 암호화
        return new BCryptPasswordEncoder();
    }
}
