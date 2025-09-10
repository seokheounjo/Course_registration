package com.example.registrationweb.repository;

import com.example.registrationweb.model.Professor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProfessorRepository extends JpaRepository<Professor, Long> {
    // 이름으로 검색 (부분 일치)
    Page<Professor> findByNameContainingIgnoreCase(String name, Pageable pageable);
    
    // 학과별 조회
    Page<Professor> findByDepartmentContainingIgnoreCase(String department, Pageable pageable);
    
    // 복합 검색
    @Query("SELECT p FROM Professor p WHERE " +
           "(:name IS NULL OR LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))) AND " +
           "(:department IS NULL OR LOWER(p.department) LIKE LOWER(CONCAT('%', :department, '%')))")
    Page<Professor> findProfessorsWithFilters(@Param("name") String name, 
                                            @Param("department") String department, 
                                            Pageable pageable);
}