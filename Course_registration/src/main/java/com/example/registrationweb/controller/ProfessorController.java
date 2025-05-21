package com.example.registrationweb.controller;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.service.ProfessorService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/professors")
public class ProfessorController {

    private final ProfessorService professorService;

    public ProfessorController(ProfessorService professorService) {
        this.professorService = professorService;
    }

    @GetMapping
    public String listProfessors(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("professors", professorService.getAllProfessors());
        return "professors/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 빈 Professor 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", "");
        model.addAttribute("name", "");
        model.addAttribute("department", "");
        model.addAttribute("email", "");
        model.addAttribute("phone", "");
        model.addAttribute("isNew", true);

        return "professors/form";
    }

    @PostMapping
    public String saveProfessor(@ModelAttribute Professor professor, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        professorService.saveProfessor(professor);
        return "redirect:/professors";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Professor professor = professorService.getProfessorById(id);

        // Professor 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", professor.getId());
        model.addAttribute("name", professor.getName());
        model.addAttribute("department", professor.getDepartment());
        model.addAttribute("email", professor.getEmail());
        model.addAttribute("phone", professor.getPhone());
        model.addAttribute("isNew", false);

        return "professors/form";
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
        return "redirect:/professors";
    }

    @GetMapping("/{id}/delete")
    public String deleteProfessor(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        professorService.deleteProfessor(id);
        return "redirect:/professors";
    }
}