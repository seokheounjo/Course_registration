package com.example.registrationweb.service;

import com.example.registrationweb.repository.StudentRepository;
import com.example.registrationweb.repository.ProfessorRepository;
import com.example.registrationweb.repository.SubjectRepository;
import com.example.registrationweb.repository.EnrollmentRepository;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class DatabaseStatusService {

    private final StudentRepository studentRepository;
    private final ProfessorRepository professorRepository;
    private final SubjectRepository subjectRepository;
    private final EnrollmentRepository enrollmentRepository;

    public DatabaseStatusService(StudentRepository studentRepository,
                                ProfessorRepository professorRepository,
                                SubjectRepository subjectRepository,
                                EnrollmentRepository enrollmentRepository) {
        this.studentRepository = studentRepository;
        this.professorRepository = professorRepository;
        this.subjectRepository = subjectRepository;
        this.enrollmentRepository = enrollmentRepository;
    }

    public Map<String, Object> getDatabaseStatus() {
        Map<String, Object> status = new HashMap<>();
        
        // 각 테이블의 레코드 수 조회
        long studentCount = studentRepository.count();
        long professorCount = professorRepository.count();
        long subjectCount = subjectRepository.count();
        long enrollmentCount = enrollmentRepository.count();
        
        status.put("studentCount", studentCount);
        status.put("professorCount", professorCount);
        status.put("subjectCount", subjectCount);
        status.put("enrollmentCount", enrollmentCount);
        status.put("totalRecords", studentCount + professorCount + subjectCount + enrollmentCount);
        
        // 데이터베이스 연결 상태
        status.put("connectionStatus", "Connected");
        status.put("databaseType", "MySQL");
        
        return status;
    }
}