package com.example.registrationweb.service;

import com.example.registrationweb.model.Enrollment;
import com.example.registrationweb.model.Student;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.repository.EnrollmentRepository;
import com.example.registrationweb.repository.StudentRepository;
import com.example.registrationweb.repository.SubjectRepository;
import com.example.registrationweb.repository.TimetableRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class EnrollmentService {
    private final EnrollmentRepository enrollmentRepository;
    private final StudentRepository studentRepository;
    private final SubjectRepository subjectRepository;
    private final TimetableRepository timetableRepository;

    public EnrollmentService(EnrollmentRepository enrollmentRepository,
                             StudentRepository studentRepository,
                             SubjectRepository subjectRepository,
                             TimetableRepository timetableRepository) {
        this.enrollmentRepository = enrollmentRepository;
        this.studentRepository = studentRepository;
        this.subjectRepository = subjectRepository;
        this.timetableRepository = timetableRepository;
    }

    @Transactional(readOnly = true)
    public boolean isAlreadyEnrolledSubject(Long studentId, Long subjectId) {
        return enrollmentRepository.existsByStudentIdAndSubjectId(studentId, subjectId);
    }

    @Transactional(readOnly = true)
    public List<Enrollment> getAllEnrollments() {
        return enrollmentRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<Enrollment> getEnrollmentsByStudentId(Long studentId) {
        Optional<Student> student = studentRepository.findById(studentId);
        return student.map(enrollmentRepository::findByStudentWithDetails)
                .orElse(List.of());
    }

    @Transactional(readOnly = true)
    public Enrollment getEnrollmentById(Long id) {
        return enrollmentRepository.findById(id).orElse(null);
    }

    @Transactional(readOnly = true)
    public long getEnrollmentCountByTimetableId(Long timetableId) {
        Optional<Timetable> timetable = timetableRepository.findById(timetableId);
        return timetable.map(enrollmentRepository::countByTimetable)
                .orElse(0L);
    }

    @Transactional
    public Enrollment enrollSubject(Long studentId, Long timetableId) {
        // 학생 정보 가져오기
        Optional<Student> optionalStudent = studentRepository.findById(studentId);
        if (optionalStudent.isEmpty()) {
            return null;
        }
        Student student = optionalStudent.get();

        // 시간표 정보 가져오기
        Optional<Timetable> optionalTimetable = timetableRepository.findById(timetableId);
        if (optionalTimetable.isEmpty()) {
            return null;
        }
        Timetable timetable = optionalTimetable.get();

        // 과목 정보 가져오기
        Subject subject = timetable.getSubject();
        if (subject == null) {
            return null;
        }

        // 이미 수강 중인 과목인지 확인
        Optional<Enrollment> existingEnrollment = enrollmentRepository.findByStudentAndSubject(student, subject);
        if (existingEnrollment.isPresent()) {
            return null;
        }

        // 정원 확인
        long currentEnrollmentCount = enrollmentRepository.countByTimetable(timetable);
        if (timetable.getCapacity() != null && currentEnrollmentCount >= timetable.getCapacity()) {
            return null; // 정원 초과
        }

        // 시간 충돌 확인
        List<Enrollment> conflicts = enrollmentRepository.findTimeConflicts(
                student, timetable.getDay(), timetable.getStartTime(), timetable.getEndTime());
        if (!conflicts.isEmpty()) {
            return null;
        }

        // 수강신청 저장
        Enrollment enrollment = new Enrollment();
        enrollment.setStudent(student);
        enrollment.setSubject(subject);
        enrollment.setTimetable(timetable);

        return enrollmentRepository.save(enrollment);
    }

    @Transactional
    public boolean cancelEnrollment(Long enrollmentId) {
        if (enrollmentRepository.existsById(enrollmentId)) {
            enrollmentRepository.deleteById(enrollmentId);
            return true;
        }
        return false;
    }
}