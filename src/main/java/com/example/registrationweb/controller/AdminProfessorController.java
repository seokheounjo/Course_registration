package com.example.registrationweb.controller;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.service.ProfessorService;
import jakarta.servlet.http.HttpSession;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/admin/professors")
public class AdminProfessorController {

    private final ProfessorService professorService;

    public AdminProfessorController(ProfessorService professorService) {
        this.professorService = professorService;
    }

    @GetMapping
    public String listProfessors(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String department,
            Model model, HttpSession session) {
        
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Page<Professor> professorsPage;
        
        // 검색 조건이 있는 경우
        if ((name != null && !name.trim().isEmpty()) ||
            (department != null && !department.trim().isEmpty())) {
            professorsPage = professorService.searchProfessors(name, department, page, size, sortBy, sortDir);
        } else {
            professorsPage = professorService.getAllProfessors(page, size, sortBy, sortDir);
        }
        
        model.addAttribute("professorsPage", professorsPage);
        model.addAttribute("professors", professorsPage.getContent());
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", professorsPage.getTotalPages());
        model.addAttribute("totalItems", professorsPage.getTotalElements());
        model.addAttribute("size", size);
        model.addAttribute("sortBy", sortBy);
        model.addAttribute("sortDir", sortDir);
        model.addAttribute("reverseSortDir", sortDir.equals("asc") ? "desc" : "asc");
        
        // 검색 파라미터 유지
        model.addAttribute("searchName", name);
        model.addAttribute("searchDepartment", department);
        
        return "admin/professors/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("professor", new Professor());
        model.addAttribute("isNew", true);

        return "admin/professors/form";
    }

    @PostMapping
    public String saveProfessor(@ModelAttribute Professor professor, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        professorService.saveProfessor(professor);
        return "redirect:/admin/professors";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Professor professor = professorService.getProfessorById(id);
        if (professor == null) {
            return "redirect:/admin/professors";
        }

        model.addAttribute("professor", professor);
        model.addAttribute("isNew", false);

        return "admin/professors/form";
    }

    @PostMapping("/{id}")
    public String updateProfessor(@PathVariable Long id,
                                @ModelAttribute Professor professor,
                                HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        professorService.updateProfessor(id, professor);
        return "redirect:/admin/professors";
    }

    @GetMapping("/{id}/delete")
    public String deleteProfessor(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        professorService.deleteProfessor(id);
        return "redirect:/admin/professors";
    }
}