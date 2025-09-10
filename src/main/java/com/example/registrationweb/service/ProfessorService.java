package com.example.registrationweb.service;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.repository.ProfessorRepository;
import com.example.registrationweb.repository.SubjectRepository;
import com.example.registrationweb.repository.TimetableRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ProfessorService {
    private final ProfessorRepository professorRepository;
    private final SubjectRepository subjectRepository;
    private final TimetableRepository timetableRepository;

    public ProfessorService(ProfessorRepository professorRepository,
                            SubjectRepository subjectRepository,
                            TimetableRepository timetableRepository) {
        this.professorRepository = professorRepository;
        this.subjectRepository = subjectRepository;
        this.timetableRepository = timetableRepository;

        // 초기 데이터 로드 (DB가 비어있을 경우에만)
        if (professorRepository.count() == 0) {
            saveProfessor(new Professor(null, "김교수", "컴퓨터공학과", "kim@example.com", "010-1234-5678"));
            saveProfessor(new Professor(null, "이교수", "전자공학과", "lee@example.com", "010-2345-6789"));
            saveProfessor(new Professor(null, "박교수", "경영학과", "park@example.com", "010-3456-7890"));
        }
    }

    @Transactional(readOnly = true)
    public List<Professor> getAllProfessors() {
        return professorRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Professor getProfessorById(Long id) {
        return professorRepository.findById(id).orElse(null);
    }

    @Transactional
    public Professor saveProfessor(Professor professor) {
        return professorRepository.save(professor);
    }

    @Transactional
    public boolean deleteProfessor(Long id) {
        if (!professorRepository.existsById(id)) {
            return false;
        }

        // 교수가 담당하는 과목 목록 조회
        List<Subject> subjects = subjectRepository.findAll()
                .stream()
                .filter(subject -> subject.getProfessor() != null &&
                        subject.getProfessor().getId().equals(id))
                .toList();

        // 교수가 담당하는 시간표 목록 조회
        List<Timetable> timetables = timetableRepository.findAll()
                .stream()
                .filter(timetable -> timetable.getProfessor() != null &&
                        timetable.getProfessor().getId().equals(id))
                .toList();

        // 시간표 연결 해제 또는 삭제
        for (Timetable timetable : timetables) {
            // 시간표 삭제
            timetableRepository.delete(timetable);
        }

        // 과목 연결 해제 또는 삭제
        for (Subject subject : subjects) {
            // 과목 삭제
            subjectRepository.delete(subject);
        }

        // 교수 삭제
        professorRepository.deleteById(id);
        return true;
    }

    @Transactional
    public Professor updateProfessor(Long id, Professor professor) {
        if (professorRepository.existsById(id)) {
            professor.setId(id);
            return professorRepository.save(professor);
        }
        return null;
    }

    // 페이지네이션과 정렬을 지원하는 교수 목록 조회
    @Transactional(readOnly = true)
    public Page<Professor> getAllProfessors(int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return professorRepository.findAll(pageable);
    }

    // 복합 검색 (이름, 학과로 검색)
    @Transactional(readOnly = true)
    public Page<Professor> searchProfessors(String name, String department, 
                                          int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        // 빈 문자열을 null로 처리
        String nameParam = (name != null && !name.trim().isEmpty()) ? name : null;
        String departmentParam = (department != null && !department.trim().isEmpty()) ? department : null;
        
        return professorRepository.findProfessorsWithFilters(nameParam, departmentParam, pageable);
    }

    // 학과별 교수 조회 (페이지네이션)
    @Transactional(readOnly = true)
    public Page<Professor> getProfessorsByDepartment(String department, int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return professorRepository.findByDepartmentContainingIgnoreCase(department, pageable);
    }
}