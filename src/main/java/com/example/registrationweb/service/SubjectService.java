package com.example.registrationweb.service;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.repository.ProfessorRepository;
import com.example.registrationweb.repository.SubjectRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class SubjectService {
    private final SubjectRepository subjectRepository;
    private final ProfessorRepository professorRepository;

    public SubjectService(SubjectRepository subjectRepository, ProfessorRepository professorRepository) {
        this.subjectRepository = subjectRepository;
        this.professorRepository = professorRepository;

        // 초기 데이터는 DB 설정 후 데이터가 로드된 후에 추가합니다
    }

    @Transactional(readOnly = true)
    public List<Subject> getAllSubjects() {
        return subjectRepository.findAll();
    }
    
    @Transactional(readOnly = true)
    public Page<Subject> getAllSubjects(int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return subjectRepository.findAll(pageable);
    }

    @Transactional(readOnly = true)
    public Page<Subject> searchSubjects(String name, String code, String department, int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        if ((name == null || name.trim().isEmpty()) && 
            (code == null || code.trim().isEmpty()) && 
            (department == null || department.trim().isEmpty())) {
            return subjectRepository.findAll(pageable);
        }
        
        return subjectRepository.findByNameContainingIgnoreCaseOrCodeContainingIgnoreCaseOrDepartmentContainingIgnoreCase(
            name != null ? name : "", 
            code != null ? code : "", 
            department != null ? department : "", 
            pageable);
    }

    @Transactional(readOnly = true)
    public Subject getSubjectById(Long id) {
        return subjectRepository.findById(id).orElse(null);
    }

    @Transactional(readOnly = true)
    public Subject getSubjectByCode(String code) {
        return subjectRepository.findByCode(code).orElse(null);
    }

    @Transactional(readOnly = true)
    public boolean existsByCode(String code) {
        return subjectRepository.existsByCode(code);
    }

    @Transactional
    public Subject saveSubject(Subject subject) {
        if (subject.getProfessor() == null && subject.getProfessorId() != null) {
            professorRepository.findById(subject.getProfessorId())
                    .ifPresent(subject::setProfessor);
        }
        return subjectRepository.save(subject);
    }

    @Transactional
    public boolean deleteSubject(Long id) {
        if (subjectRepository.existsById(id)) {
            subjectRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional
    public Subject updateSubject(Long id, Subject subject) {
        if (subjectRepository.existsById(id)) {
            subject.setId(id);

            if (subject.getProfessor() == null && subject.getProfessorId() != null) {
                professorRepository.findById(subject.getProfessorId())
                        .ifPresent(subject::setProfessor);
            }

            return subjectRepository.save(subject);
        }
        return null;
    }

    // 초기 샘플 데이터 로드
    @Transactional
    public void loadSampleData() {
        if (subjectRepository.count() > 0) {
            return; // 이미 데이터가 있으면 로드하지 않음
        }

        List<Professor> professors = professorRepository.findAll();
        if (professors.size() < 3) {
            return; // 교수 데이터가 부족하면 로드하지 않음
        }

        Professor professor1 = professors.get(0); // 김교수
        Professor professor2 = professors.get(1); // 이교수
        Professor professor3 = professors.get(2); // 박교수

        Subject subject1 = new Subject(null, "CS101", "컴퓨터 개론", 3, "컴퓨터공학과", professor1);
        Subject subject2 = new Subject(null, "CS202", "자료구조", 3, "컴퓨터공학과", professor1);
        Subject subject3 = new Subject(null, "EE101", "전자공학 개론", 3, "전자공학과", professor2);
        Subject subject4 = new Subject(null, "BZ101", "경영학 원론", 3, "경영학과", professor3);

        subjectRepository.save(subject1);
        subjectRepository.save(subject2);
        subjectRepository.save(subject3);
        subjectRepository.save(subject4);
    }
}