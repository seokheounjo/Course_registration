package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Professor;
import com.example.course_registration.entity.Department;
import com.example.course_registration.repository.DepartmentRepository;
import com.example.course_registration.repository.ProfessorRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/professors")
public class ProfessorManageController {

    @Autowired
    private ProfessorRepository professorRepository;

    @Autowired
    private DepartmentRepository departmentRepository;

    // 교수 목록 조회
    @GetMapping
    public String list(Model model) {
        List<Professor> professors = professorRepository.findAll();
        model.addAttribute("professors", professors);
        return "manage/professors"; // 정확한 뷰 경로 지정
    }

    // 교수 등록 폼
    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("professor", new Professor());
        List<Department> departments = departmentRepository.findAll();
        model.addAttribute("departments", departments);
        return "manage/professor_form";
    }

    // 교수 수정 폼
    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable("id") Long id, Model model) {
        Professor professor = professorRepository.findById(id).orElseThrow();
        model.addAttribute("professor", professor);
        List<Department> departments = departmentRepository.findAll();
        model.addAttribute("departments", departments);
        return "manage/professor_form";
    }

    // 교수 저장 (등록/수정)
    @PostMapping("/save")
    public String save(@ModelAttribute Professor professor, @RequestParam Long departmentId) {
        Department department = departmentRepository.findById(departmentId).orElseThrow();
        professor.setDepartment(department);
        professorRepository.save(professor);
        return "redirect:/admin/professors"; // 저장 후 리디렉션
    }

    // 교수 삭제
    @Transactional
    @GetMapping("/delete/{id}")
    public String delete(@PathVariable("id") Long id) {
        professorRepository.deleteById(id); // ON DELETE CASCADE가 설정되어 있어야 함
        return "redirect:/admin/professors"; // 삭제 후 리디렉션
    }
}
