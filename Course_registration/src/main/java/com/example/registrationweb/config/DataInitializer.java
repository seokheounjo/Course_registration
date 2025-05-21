package com.example.registrationweb.config;

import com.example.registrationweb.service.ProfessorService;
import com.example.registrationweb.service.StudentService;
import com.example.registrationweb.service.SubjectService;
import com.example.registrationweb.service.TimetableService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    public CommandLineRunner loadData(StudentService studentService,
                                      ProfessorService professorService,
                                      SubjectService subjectService,
                                      TimetableService timetableService) {
        return args -> {
            // 순서대로 데이터 로드
            // 1. 교수 데이터는 ProfessorService 생성자에서 로드
            // 2. 학생 데이터는 StudentService 생성자에서 로드
            // 3. 과목 데이터 로드
            subjectService.loadSampleData();
            // 4. 시간표 데이터 로드
            timetableService.loadSampleData();

            System.out.println("샘플 데이터 로드 완료");
        };
    }
}