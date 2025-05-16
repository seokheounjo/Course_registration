package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Department;
import com.example.course_registration.repository.DepartmentRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/departments")
public class DepartmentManageController {

    private final DepartmentRepository repo;

    public DepartmentManageController(DepartmentRepository repo) {
        this.repo = repo;
    }

    // 목록 & 검색 (keyword 항상 빈 문자열이라도 넣음)
    @GetMapping
    public String list(Model model,
                       @RequestParam(value="keyword", required=false) String keyword) {
        String kw = (keyword == null ? "" : keyword.trim());
        List<Department> list = kw.isEmpty()
                ? repo.findAll()
                : repo.findByNameContaining(kw);
        model.addAttribute("departments", list);
        model.addAttribute("keyword", kw);
        return "manage/departments";
    }

    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("department", new Department());
        return "manage/department_form";
    }

    @PostMapping("/add")
    public String addSubmit(Department department) {
        repo.save(department);
        return "redirect:/admin/departments";
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        Department d = repo.findById(id).orElseThrow();
        model.addAttribute("department", d);
        return "manage/department_form";
    }

    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id, Department department) {
        department.setId(id);
        repo.save(department);
        return "redirect:/admin/departments";
    }

    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        repo.deleteById(id);
        return "redirect:/admin/departments";
    }
}
