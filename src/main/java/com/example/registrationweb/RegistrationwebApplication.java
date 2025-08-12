package com.example.registrationweb;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RegistrationwebApplication {

	public static void main(String[] args) {
		SpringApplication.run(RegistrationwebApplication.class, args);
	}

	// Spring Boot 3.x는 자동으로 character encoding을 구성합니다
	// 추가 필터가 필요하지 않습니다
}