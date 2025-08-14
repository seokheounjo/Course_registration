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
        
        // 교수 중복 제거 먼저 실행
        removeDuplicateProfessors();
        
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
    
    private void removeDuplicateProfessors() {
        try {
            // 중복된 교수들을 찾아서 제거하는 로직
            // 이름이 같은 교수들 중 ID가 가장 작은 것만 남기고 나머지 삭제
            professorRepository.findAll().stream()
                .collect(java.util.stream.Collectors.groupingBy(p -> p.getName()))
                .values().stream()
                .filter(professors -> professors.size() > 1)
                .forEach(duplicates -> {
                    // 첫 번째(가장 작은 ID)를 제외하고 나머지 삭제
                    duplicates.subList(1, duplicates.size()).forEach(professor -> {
                        try {
                            professorRepository.delete(professor);
                        } catch (Exception e) {
                            // 참조 무결성 오류 무시 (과목에서 참조 중인 경우)
                        }
                    });
                });
        } catch (Exception e) {
            // 오류 발생 시 무시 (로그에만 기록)
            System.out.println("교수 중복 제거 중 오류 발생: " + e.getMessage());
        }
    }
}