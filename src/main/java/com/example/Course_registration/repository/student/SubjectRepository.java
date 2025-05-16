package com.example.Course_registration.repository.student;

import com.example.Course_registration.entity.student.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SubjectRepository extends JpaRepository<Subject, Long> {
    // 필요한 경우 과목 검색용 메서드 추가 가능
}
