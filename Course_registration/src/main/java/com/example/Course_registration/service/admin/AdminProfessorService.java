package com.example.Course_registration.service.admin;

import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.repository.ProfessorRepository;
import com.example.Course_registration.repository.SubjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminProfessorService {

    private final ProfessorRepository professorRepository;
    private final SubjectRepository subjectRepository;

    // 🔽 교수 목록 조회
    public List<Professor> findAll() {
        return professorRepository.findAll();
    }

    // 🔽 교수 삭제 (과목 참조 제거 후 삭제)
    @Transactional
    public void delete(Long id) {
        List<Subject> subjects = subjectRepository.findByProfessorId(id);
        for (Subject subject : subjects) {
            subject.setProfessor(null);
        }
        professorRepository.deleteById(id);
    }

    // 🔽 교수 ID로 조회
    public Professor findById(Long id) {
        return professorRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("교수를 찾을 수 없습니다. ID: " + id));
    }

    // 🔽 교수 저장 (신규 vs 수정)
    @Transactional
    public void save(Professor professor) {
        if (professor.getId() == null) {
            // 신규 저장 (id 없음 → JPA가 자동 생성)
            professorRepository.save(professor);
        } else {
            // 수정 저장 (기존 엔티티 불러와 필드만 갱신)
            Professor existing = professorRepository.findById(professor.getId())
                    .orElseThrow(() -> new IllegalArgumentException("수정할 교수 정보가 없습니다. ID: " + professor.getId()));

            existing.setName(professor.getName());
            existing.setEmail(professor.getEmail());
            existing.setPassword(professor.getPassword());
            existing.setDepartment(professor.getDepartment());
            // 저장 생략 가능: @Transactional + 영속 엔티티 자동 dirty checking
        }
    }
}
