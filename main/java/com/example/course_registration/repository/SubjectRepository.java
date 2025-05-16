// src/main/java/com/example/Course_registration/repository/SubjectRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SubjectRepository extends JpaRepository<Subject, Long> {
    List<Subject> findByDepartmentId(Long deptId);
    List<Subject> findByProfessorId(Long profId);
    List<Subject> findBySemester(String semester);
}
