package com.example.Course_registration.Service;

import com.example.Course_registration.entity.Admin;
import com.example.Course_registration.entity.Student;
import com.example.Course_registration.repository.AdminRepository;
import com.example.Course_registration.repository.StudentRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class LoginService {

    private final StudentRepository studentRepository;
    private final AdminRepository adminRepository;

    public LoginService(StudentRepository studentRepository,
                        AdminRepository adminRepository) {
        this.studentRepository = studentRepository;
        this.adminRepository = adminRepository;
    }

    public Optional<Object> authenticate(String userId, String password) {
        System.out.println("🧪 로그인 시도 → ID: " + userId + ", PW: " + password);

        // 1) 관리자 로그인 (하드코딩)
        if ("admin01".equals(userId) && "admin01".equals(password)) {
            Admin dummyAdmin = new Admin();
            dummyAdmin.setId(1L);
            dummyAdmin.setUsername("admin01");
            dummyAdmin.setPassword("admin01");
            dummyAdmin.setName("관리자");
            return Optional.of(dummyAdmin);
        }

        // 2) 학생 로그인
        Student student = studentRepository.findByStudentNumber(userId);
        if (student != null) {
            System.out.println("🧾 DB 비번: " + student.getPassword());
            if (student.getPassword().equals(password)) {
                System.out.println("✅ 학생 로그인 성공");
                return Optional.of(student);
            } else {
                System.out.println("❌ 비밀번호 불일치");
            }
        } else {
            System.out.println("❌ 학생 번호 없음");
        }

        return Optional.empty();
    }
}
