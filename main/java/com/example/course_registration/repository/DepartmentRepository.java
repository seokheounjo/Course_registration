// src/main/java/com/example/course_registration/repository/DepartmentRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DepartmentRepository extends JpaRepository<Department, Long> {
    // Add the search method here
    List<Department> findByNameContaining(String name);
}
