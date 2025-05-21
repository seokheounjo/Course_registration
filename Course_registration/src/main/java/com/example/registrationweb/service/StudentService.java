package com.example.registrationweb.service;

import com.example.registrationweb.model.Student;
import com.example.registrationweb.repository.StudentRepository;
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
}