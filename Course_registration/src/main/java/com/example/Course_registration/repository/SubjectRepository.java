package com.example.Course_registration.repository;

import com.example.Course_registration.entity.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface SubjectRepository extends JpaRepository<Subject, Long> {
    List<Subject> findByProfessorIsNull();

    // [추가] 특정 교수의 과목 전체 조회
    List<Subject> findByProfessorId(Long professorId);

    @Query("SELECT s FROM Subject s " +
            "WHERE (:professorId IS NULL OR s.professor.id = :professorId) " +
            "AND (:departmentId IS NULL OR s.department.id = :departmentId) " +
            "AND (:grade IS NULL OR s.department.name LIKE CONCAT('%', :grade, '%'))")
    List<Subject> searchWithConditions(@Param("professorId") Long professorId,
                                       @Param("departmentId") Long departmentId,
                                       @Param("grade") String grade);

}
