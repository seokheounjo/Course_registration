// repository 수정: student가 신청한 과목 ID 조회 메서드 추가
package com.example.Course_registration.repository.student;

import com.example.Course_registration.entity.student.Enrollment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    boolean existsByStudentIdAndSubjectId(Long studentId, Long subjectId);

    int countBySubjectId(Long subjectId);

    // 추가: 특정 학생이 신청한 과목 ID 목록
    @Query("SELECT e.subjectId FROM Enrollment e WHERE e.studentId = :studentId")
    List<Long> findSubjectIdsByStudentId(Long studentId);

    // 추가: 특정 학생이 신청한 전체 수강신청 정보 (수강 내역 출력용)
    List<Enrollment> findByStudentId(Long studentId);

    // (선택) 삭제 기능: 수강 취소용
    void deleteByStudentIdAndSubjectId(Long studentId, Long subjectId);
}
