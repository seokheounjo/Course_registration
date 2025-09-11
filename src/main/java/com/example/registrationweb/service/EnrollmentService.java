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
        System.out.println("DEBUG ENROLLMENT: Getting enrollments for student ID: " + studentId);
        Optional<Student> studentOpt = studentRepository.findById(studentId);
        if (studentOpt.isEmpty()) {
            System.out.println("DEBUG ENROLLMENT: Student not found for ID: " + studentId);
            return List.of();
        }
        
        Student student = studentOpt.get();
        List<Enrollment> enrollments = enrollmentRepository.findByStudentWithDetails(student);
        System.out.println("DEBUG ENROLLMENT: Found " + enrollments.size() + " enrollments");
        
        for (Enrollment enrollment : enrollments) {
            System.out.println("DEBUG ENROLLMENT: - Subject: " + 
                (enrollment.getSubject() != null ? enrollment.getSubject().getName() : "NULL") +
                ", Timetable: " + (enrollment.getTimetable() != null ? enrollment.getTimetable().getDay() : "NULL"));
        }
        
        return enrollments;
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
        System.out.println("DEBUG ENROLLMENT: Starting enrollment - StudentID: " + studentId + ", TimetableID: " + timetableId);
        
        // 학생 정보 가져오기
        Optional<Student> optionalStudent = studentRepository.findById(studentId);
        if (optionalStudent.isEmpty()) {
            System.out.println("DEBUG ENROLLMENT: Student not found");
            return null;
        }
        Student student = optionalStudent.get();
        System.out.println("DEBUG ENROLLMENT: Student found - " + student.getName());

        // 시간표 정보 가져오기
        Optional<Timetable> optionalTimetable = timetableRepository.findById(timetableId);
        if (optionalTimetable.isEmpty()) {
            System.out.println("DEBUG ENROLLMENT: Timetable not found");
            return null;
        }
        Timetable timetable = optionalTimetable.get();
        System.out.println("DEBUG ENROLLMENT: Timetable found - " + timetable.getSubjectName());

        // 과목 정보 가져오기
        Subject subject = timetable.getSubject();
        if (subject == null) {
            System.out.println("DEBUG ENROLLMENT: Subject is null in timetable");
            return null;
        }
        System.out.println("DEBUG ENROLLMENT: Subject found - " + subject.getName());

        // 이미 수강 중인 과목인지 확인
        Optional<Enrollment> existingEnrollment = enrollmentRepository.findByStudentAndSubject(student, subject);
        if (existingEnrollment.isPresent()) {
            System.out.println("DEBUG ENROLLMENT: Already enrolled in this subject");
            return null;
        }

        // 정원 확인
        long currentEnrollmentCount = enrollmentRepository.countByTimetable(timetable);
        if (timetable.getCapacity() != null && currentEnrollmentCount >= timetable.getCapacity()) {
            System.out.println("DEBUG ENROLLMENT: Capacity exceeded - " + currentEnrollmentCount + "/" + timetable.getCapacity());
            return null; // 정원 초과
        }

        // 시간 충돌 확인
        List<Enrollment> conflicts = enrollmentRepository.findTimeConflicts(
                student, timetable.getDay(), timetable.getStartTime(), timetable.getEndTime());
        if (!conflicts.isEmpty()) {
            System.out.println("DEBUG ENROLLMENT: Time conflict found");
            return null;
        }

        // 수강신청 저장
        Enrollment enrollment = new Enrollment();
        enrollment.setStudent(student);
        enrollment.setSubject(subject);
        enrollment.setTimetable(timetable);

        Enrollment saved = enrollmentRepository.save(enrollment);
        System.out.println("DEBUG ENROLLMENT: Successfully saved enrollment with ID: " + saved.getId());
        return saved;
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