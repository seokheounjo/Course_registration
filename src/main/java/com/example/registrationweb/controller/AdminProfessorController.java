package com.example.registrationweb.controller;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.service.ProfessorService;
import jakarta.servlet.http.HttpSession;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/professors")
public class AdminProfessorController {

    private final ProfessorService professorService;

    public AdminProfessorController(ProfessorService professorService) {
        this.professorService = professorService;
    }

    @GetMapping
    public String listProfessors(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 가장 단순한 형태로 테스트
        try {
            List<Professor> professors = professorService.getAllProfessors();
            model.addAttribute("professors", professors);
            model.addAttribute("totalItems", professors.size());
            model.addAttribute("totalPages", 1);
            model.addAttribute("currentPage", 0);
            model.addAttribute("currentPageDisplay", 1);
            model.addAttribute("hasPrevious", false);
            model.addAttribute("hasNext", false);
            model.addAttribute("size", 20);
            model.addAttribute("sortBy", "name");
            model.addAttribute("sortDir", "asc");
            model.addAttribute("reverseSortDir", "desc");
            model.addAttribute("startItem", 1);
            model.addAttribute("endItem", professors.size());
            model.addAttribute("searchName", "");
            model.addAttribute("searchDepartment", "");
            
            return "admin/professors/list";
        } catch (Exception e) {
            model.addAttribute("error", "Error: " + e.getMessage());
            return "error";
        }
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