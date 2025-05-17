// 6. AdminRepository.java
package com.example.Course_registration.repository;

import com.example.Course_registration.entity.Admin;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AdminRepository extends JpaRepository<Admin, Long> {
    Admin findByUsername(String username);
}