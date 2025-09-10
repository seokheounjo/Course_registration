package com.example.registrationweb.service;

import com.example.registrationweb.model.Student;
import com.example.registrationweb.repository.StudentRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class StudentService {
    private final StudentRepository studentRepository;

    public StudentService(StudentRepository studentRepository) {
        this.studentRepository = studentRepository;

        // 초기 데이터 로드 (DB가 비어있을 경우에만)
        if (studentRepository.count() == 0) {
            saveStudent(new Student(null, "20250095", "김규석", "컴퓨터공학과", "20250095", "1"));
            saveStudent(new Student(null, "20250096", "김철수", "전자공학과", "20250096", "2"));
            saveStudent(new Student(null, "20250097", "이영희", "경영학과", "20250097", "3"));
        }
    }

    @Transactional(readOnly = true)
    public List<Student> getAllStudents() {
        return studentRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Student getStudentById(Long id) {
        return studentRepository.findById(id).orElse(null);
    }

    @Transactional(readOnly = true)
    public Student getStudentByStudentId(String studentId) {
        return studentRepository.findByStudentId(studentId).orElse(null);
    }

    @Transactional
    public Student saveStudent(Student student) {
        return studentRepository.save(student);
    }

    @Transactional
    public boolean deleteStudent(Long id) {
        if (studentRepository.existsById(id)) {
            studentRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional
    public Student updateStudent(Long id, Student student) {
        if (studentRepository.existsById(id)) {
            student.setId(id);
            return studentRepository.save(student);
        }
        return null;
    }

    @Transactional(readOnly = true)
    public Student validateStudent(String studentId, String password) {
        Optional<Student> student = studentRepository.findByStudentId(studentId);
        if (student.isPresent() && student.get().getPassword().equals(password)) {
            return student.get();
        }
        return null;
    }

    // 페이지네이션과 정렬을 지원하는 학생 목록 조회
    @Transactional(readOnly = true)
    public Page<Student> getAllStudents(int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return studentRepository.findAll(pageable);
    }

    // 학년별 학생 조회 (페이지네이션)
    @Transactional(readOnly = true)
    public Page<Student> getStudentsByGrade(String grade, int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return studentRepository.findByGrade(grade, pageable);
    }

    // 복합 검색 (이름, 학번, 학년으로 검색)
    @Transactional(readOnly = true)
    public Page<Student> searchStudents(String grade, String name, String studentId, 
                                       int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        // 빈 문자열을 null로 처리
        String gradeParam = (grade != null && !grade.trim().isEmpty()) ? grade : null;
        String nameParam = (name != null && !name.trim().isEmpty()) ? name : null;
        String studentIdParam = (studentId != null && !studentId.trim().isEmpty()) ? studentId : null;
        
        return studentRepository.findStudentsWithFilters(gradeParam, nameParam, studentIdParam, pageable);
    }

    // 학년별 학생 수 조회
    @Transactional(readOnly = true)
    public List<Student> getStudentsByGrade(String grade) {
        return studentRepository.findByGrade(grade);
    }

    // 학과별 학생 조회 (페이지네이션)
    @Transactional(readOnly = true)
    public Page<Student> getStudentsByDepartment(String department, int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return studentRepository.findByDepartmentContainingIgnoreCase(department, pageable);
    }
}