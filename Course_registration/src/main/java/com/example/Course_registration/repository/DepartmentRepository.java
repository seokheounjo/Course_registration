package com.example.Course_registration.repository;

import com.example.Course_registration.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository               // ← 생략해도 무방하지만 명시 권장
public interface DepartmentRepository
        extends JpaRepository<Department, Long> {
    // 추가 검색 메서드가 필요하면 여기에 선언
}
