package com.example.course_registration.repository;

import com.example.course_registration.entity.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SubjectRepository extends JpaRepository<Subject, Long> {
    // 이름에 키워드가 포함된 과목을 검색하는 메서드
    List<Subject> findByNameContaining(String keyword);
}
