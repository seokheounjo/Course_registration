package com.example.Course_registration.repository;

import com.example.Course_registration.entity.Student;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentRepository extends JpaRepository<Student, Long> {
    Student findByStudentNumber(String studentNumber);
}


