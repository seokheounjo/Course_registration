package com.example.registrationweb.repository;

import com.example.registrationweb.model.Student;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;
import java.util.Optional;

public interface StudentRepository extends JpaRepository<Student, Long> {
    Optional<Student> findByStudentId(String studentId);
    boolean existsByStudentId(String studentId);
    
    // 학년별 조회
    Page<Student> findByGrade(String grade, Pageable pageable);
    List<Student> findByGrade(String grade);
    
    // 이름으로 검색 (부분 일치)
    Page<Student> findByNameContainingIgnoreCase(String name, Pageable pageable);
    
    // 학번으로 검색 (부분 일치)
    Page<Student> findByStudentIdContaining(String studentId, Pageable pageable);
    
    // 복합 검색
    @Query("SELECT s FROM Student s WHERE " +
           "(:grade IS NULL OR s.grade = :grade) AND " +
           "(:name IS NULL OR LOWER(s.name) LIKE LOWER(CONCAT('%', :name, '%'))) AND " +
           "(:studentId IS NULL OR s.studentId LIKE CONCAT('%', :studentId, '%'))")
    Page<Student> findStudentsWithFilters(@Param("grade") String grade, 
                                         @Param("name") String name, 
                                         @Param("studentId") String studentId, 
                                         Pageable pageable);
    
    // 학과별 조회
    Page<Student> findByDepartmentContainingIgnoreCase(String department, Pageable pageable);
}