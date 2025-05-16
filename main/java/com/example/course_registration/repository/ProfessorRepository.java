// src/main/java/com/example/course_registration/repository/ProfessorRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.Professor;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ProfessorRepository extends JpaRepository<Professor, Long> {
    List<Professor> findByDepartmentId(Long departmentId);
}
