package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Student;
import com.example.course_registration.repository.StudentRepository;
import com.example.course_registration.repository.DepartmentRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/students")
public class StudentManageController {

    private final StudentRepository stuRepo;
    private final DepartmentRepository deptRepo;

    public StudentManageController(StudentRepository stuRepo,
                                   DepartmentRepository deptRepo) {
        this.stuRepo = stuRepo;
        this.deptRepo = deptRepo;
    }

    // 목록 (옵션: 학과/학년 filter)
    @GetMapping
    public String list(Model model,
                       @RequestParam(value="deptId", required=false) Long deptId,
                       @RequestParam(value="grade", required=false) String grade) {
        List<Student> list;
        if(deptId != null) {
            list = stuRepo.findByDepartmentId(deptId);
        } else if(grade != null && !grade.isBlank()) {
            list = stuRepo.findByGrade(grade);
        } else {
            list = stuRepo.findAll();
        }
        model.addAttribute("students", list);
        model.addAttribute("departments", deptRepo.findAll());
        model.addAttribute("selectedDept", deptId);
        model.addAttribute("selectedGrade", grade);
        return "manage/students";
    }

    // 추가 폼
    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("student", new Student());
        model.addAttribute("departments", deptRepo.findAll());
        return "manage/student_form";
    }

    // 추가 처리
    @PostMapping("/add")
    public String addSubmit(Student student) {
        stuRepo.save(student);
        return "redirect:/admin/students";
    }

    // 수정 폼
    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        Student s = stuRepo.findById(id).orElseThrow();
        model.addAttribute("student", s);
        model.addAttribute("departments", deptRepo.findAll());
        return "manage/student_form";
    }

    // 수정 처리
    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id, Student student) {
        student.setId(id);
        stuRepo.save(student);
        return "redirect:/admin/students";
    }

    // 삭제
    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        stuRepo.deleteById(id);
        return "redirect:/admin/students";
    }
}
