package com.example.Course_registration.Service;

import com.example.Course_registration.entity.Admin;
import com.example.Course_registration.entity.Student;
import com.example.Course_registration.repository.AdminRepository;
import com.example.Course_registration.repository.StudentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private StudentRepository studentRepository;

    @Autowired
    private AdminRepository adminRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        Student student = studentRepository.findByStudentNumber(username);
        if (student != null) {
            return User.builder()
                    .username(student.getStudentNumber())
                    .password(student.getPassword())
                    .roles("STUDENT")
                    .build();
        }

        Admin admin = adminRepository.findByUsername(username);
        if (admin != null) {
            return User.builder()
                    .username(admin.getUsername())
                    .password(admin.getPassword())
                    .roles("ADMIN")
                    .build();
        }

        throw new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + username);
    }
}
