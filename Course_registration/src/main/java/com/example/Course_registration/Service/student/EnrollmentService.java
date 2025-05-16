package com.example.Course_registration.Service.student;

import com.example.Course_registration.entity.student.Enrollment;
import com.example.Course_registration.entity.student.Subject;
import com.example.Course_registration.repository.student.EnrollmentRepository;
import com.example.Course_registration.repository.student.SubjectRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class EnrollmentService {

    @Autowired
    private EnrollmentRepository enrollmentRepository;

    @Autowired
    private SubjectRepository subjectRepository;

    public String enrollStudent(Long studentId, Long subjectId) {
        boolean alreadyEnrolled = enrollmentRepository.existsByStudentIdAndSubjectId(studentId, subjectId);
        if (alreadyEnrolled) {
            return "이미 수강 신청한 과목입니다.";
        }

        Optional<Subject> subjectOpt = subjectRepository.findById(subjectId);
        if (subjectOpt.isEmpty()) {
            return "과목이 존재하지 않습니다.";
        }

        Subject subject = subjectOpt.get();
        int enrolledCount = enrollmentRepository.countBySubjectId(subjectId);
        if (enrolledCount >= subject.getCapacity()) {
            return "수강 정원이 초과되었습니다.";
        }

        Enrollment enrollment = new Enrollment(studentId, subjectId);
        enrollmentRepository.save(enrollment);

        return "수강 신청이 완료되었습니다.";
    }

    // 수강 취소 기능 추가
    public void cancelEnrollment(Long studentId, Long subjectId) {
        enrollmentRepository.deleteByStudentIdAndSubjectId(studentId, subjectId);
    }
}
