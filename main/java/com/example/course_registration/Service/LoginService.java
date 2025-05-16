package com.example.course_registration.service;

import com.example.course_registration.entity.Student;               // <-- 수정된 경로
import com.example.course_registration.repository.ProfessorRepository;
import com.example.course_registration.repository.StudentRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class LoginService {

    private final StudentRepository studentRepository;
    private final ProfessorRepository professorRepository;

    public LoginService(StudentRepository studentRepository,
                        ProfessorRepository professorRepository) {
        this.studentRepository = studentRepository;
        this.professorRepository = professorRepository;
    }

    /**
     * 1) 임시 관리자 하드코딩
     * 2) 학생(student_number) 로그인
     * 3) (추후) 교수 테이블 기반 관리자 로그인
     */
    public Optional<String> authenticate(String userId, String password) {
        // 1) 임시 관리자 계정
        if ("admin01".equals(userId) && "admin01".equals(password)) {
            return Optional.of("ADMIN");
        }

        // 2) 학생 인증
        Student student = studentRepository.findByStudentNumber(userId);
        if (student != null && student.getPassword().equals(password)) {
            return Optional.of("STUDENT");
        }

        // 3) (추후) 교수 인증
        // -- 생략 --

        // 모두 실패
        return Optional.empty();
    }
}
