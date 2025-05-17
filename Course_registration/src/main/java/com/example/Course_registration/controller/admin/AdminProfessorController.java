package com.example.Course_registration.controller.admin;

import com.example.Course_registration.dto.DepartmentDTO;
import com.example.Course_registration.dto.ProfessorForm;
import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.repository.DepartmentRepository;
import com.example.Course_registration.service.admin.AdminProfessorService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/admin/professors")
@RequiredArgsConstructor
public class AdminProfessorController {

    private final AdminProfessorService professorService;
    private final DepartmentRepository departmentRepository;

    // 교수 목록
    @GetMapping
    public String list(Model model) {
        List<Professor> professors = professorService.findAll();
        model.addAttribute("professors", professors);
        return "admin/professor/list";
    }

    // 신규 등록 폼
    @GetMapping("/new")
    public String newForm(Model model) {
        Professor prof = new Professor();

        // 루트에 직접 키를 풀어서 넣기
        model.addAttribute("id", null);
        model.addAttribute("name", "");
        model.addAttribute("email", "");
        model.addAttribute("password", "");
        model.addAttribute("departmentId", null);

        model.addAttribute("departments", departmentRepository.findAll());
        return "admin/professor/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        Professor prof = professorService.findById(id);

        model.addAttribute("id", prof.getId());
        model.addAttribute("name", prof.getName());
        model.addAttribute("email", prof.getEmail());
        model.addAttribute("password", prof.getPassword());
        model.addAttribute("departmentId", prof.getDepartment() != null ? prof.getDepartment().getId() : null);

        // selected 처리
        List<Department> allDeps = departmentRepository.findAll();
        List<Map<String, Object>> deps = allDeps.stream().map(dep -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", dep.getId());
            map.put("name", dep.getName());
            map.put("selected", dep.getId().equals(prof.getDepartment().getId()));
            return map;
        }).collect(Collectors.toList());

        model.addAttribute("departments", deps);

        return "admin/professor/form";
    }





    @PostMapping
    public String create(@RequestParam String name,
                         @RequestParam String email,
                         @RequestParam String password,
                         @RequestParam Long departmentId) {

        Professor p = new Professor();
        p.setName(name);
        p.setEmail(email);
        p.setPassword(password);
        p.setDepartment(departmentRepository.findById(departmentId).orElse(null));

        // 🔥 여기에 id는 명시적으로 null이어야 함
        // p.setId(null); ← 혹시 이전에 setId(1) 같은 게 들어갔다면 지워야 함

        professorService.save(p);
        return "redirect:/admin/professors";
    }


    // 수정 폼


    // 수정 처리
    @PostMapping("/{id}/edit")
    public String update(@PathVariable Long id, @ModelAttribute ProfessorForm form) {
        Department department = departmentRepository.findById(form.getDepartmentId()).orElse(null);
        Professor updatedProfessor = form.toEntity(department);
        updatedProfessor.setId(id);
        professorService.save(updatedProfessor);
        return "redirect:/admin/professors";
    }

    // 삭제 처리
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        professorService.delete(id);
        return "redirect:/admin/professors";
    }
}
