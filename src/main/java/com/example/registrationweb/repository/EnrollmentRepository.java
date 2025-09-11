package com.example.registrationweb.repository;

import com.example.registrationweb.model.Enrollment;
import com.example.registrationweb.model.Student;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;
import java.util.Optional;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {
    @Query("SELECT e FROM Enrollment e " +
           "LEFT JOIN FETCH e.subject s " +
           "LEFT JOIN FETCH s.professor " +
           "LEFT JOIN FETCH e.timetable " +
           "WHERE e.student = :student")
    List<Enrollment> findByStudentWithDetails(@Param("student") Student student);
    
    List<Enrollment> findByStudent(Student student);

    long countByTimetable(Timetable timetable);

    Optional<Enrollment> findByStudentAndSubject(Student student, Subject subject);

    // 새로 추가된 메서드
    @Query("SELECT COUNT(e) > 0 FROM Enrollment e WHERE e.student.id = :studentId AND e.subject.id = :subjectId")
    boolean existsByStudentIdAndSubjectId(@Param("studentId") Long studentId, @Param("subjectId") Long subjectId);

    @Query("SELECT e FROM Enrollment e WHERE e.student = ?1 AND e.timetable.day = ?2 " +
            "AND ((e.timetable.startTime <= ?3 AND e.timetable.endTime > ?3) " +
            "OR (e.timetable.startTime < ?4 AND e.timetable.endTime >= ?4) " +
            "OR (e.timetable.startTime >= ?3 AND e.timetable.endTime <= ?4))")
    List<Enrollment> findTimeConflicts(Student student, String day, String startTime, String endTime);
}