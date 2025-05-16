// src/main/java/com/example/Course_registration/repository/SubjectScheduleRepository.java
package com.example.course_registration.repository;

import com.example.course_registration.entity.SubjectSchedule;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SubjectScheduleRepository extends JpaRepository<SubjectSchedule, Long> {
    List<SubjectSchedule> findBySubjectId(Long subjectId);
}
