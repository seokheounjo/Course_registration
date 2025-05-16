// src/main/java/com/example/Course_registration/repository/StudentRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.Student;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface StudentRepository extends JpaRepository<Student, Long> {
    Student findByStudentNumber(String studentNumber);
    List<Student> findByDepartmentId(Long deptId);
    List<Student> findByGrade(String grade);
}
