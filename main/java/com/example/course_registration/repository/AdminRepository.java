// 6. AdminRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.Admin;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AdminRepository extends JpaRepository<Admin, Long> {
    Admin findByUsername(String username);
}