package com.example.Course_registration.service.admin;

import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.repository.SubjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminSubjectService {

    private final SubjectRepository subjectRepository;

    public List<Subject> findAll() {
        return subjectRepository.findAll();
    }

    public Subject findById(Long id) {
        return subjectRepository.findById(id).orElseThrow();
    }

    public Subject save(Subject subject) {
        return subjectRepository.save(subject);
    }

    public void delete(Long id) {
        subjectRepository.deleteById(id);
    }
    public List<Subject> searchSubjects(Long professorId, Long departmentId, String grade) {
        return subjectRepository.searchWithConditions(professorId, departmentId, grade);
    }

}
