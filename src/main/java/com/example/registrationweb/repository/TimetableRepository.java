package com.example.registrationweb.repository;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;

public interface TimetableRepository extends JpaRepository<Timetable, Long> {
    List<Timetable> findBySubject(Subject subject);
    List<Timetable> findByProfessor(Professor professor);
    @Query("SELECT t FROM Timetable t " +
           "LEFT JOIN FETCH t.subject s " +
           "LEFT JOIN FETCH s.professor p " +
           "LEFT JOIN FETCH t.professor")
    List<Timetable> findAllWithDetails();
    
    Page<Timetable> findBySubjectNameContainingIgnoreCaseOrDayContainingIgnoreCaseOrRoomContainingIgnoreCase(
            String subjectName, String day, String room, Pageable pageable);
    Page<Timetable> findByDayContainingIgnoreCaseOrRoomContainingIgnoreCase(
            String day, String room, Pageable pageable);
}