package com.example.Course_registration.repository;

import com.example.Course_registration.entity.Enrollment;
import com.example.Course_registration.entity.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    List<Enrollment> findByStudentId(Long studentId);

    boolean existsByStudentIdAndSubjectId(Long studentId, Long subjectId);

    void deleteByStudentIdAndSubjectId(Long studentId, Long subjectId);

    int countBySubjectId(Long subjectId);

    // ✅ 정확히 수정된 쿼리
    @Query("SELECT e.subject.id FROM Enrollment e WHERE e.student.id = :studentId")
    List<Long> findSubjectIdsByStudentId(@Param("studentId") Long studentId);
}
