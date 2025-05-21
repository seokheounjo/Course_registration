package com.example.registrationweb.controller;

import com.example.registrationweb.model.Subject;
import com.example.registrationweb.service.ProfessorService;
import com.example.registrationweb.service.SubjectService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/subjects")
public class SubjectController {

    private final SubjectService subjectService;
    private final ProfessorService professorService;

    public SubjectController(SubjectService subjectService, ProfessorService professorService) {
        this.subjectService = subjectService;
        this.professorService = professorService;
    }

    @GetMapping
    public String listSubjects(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("subjects", subjectService.getAllSubjects());
        return "subjects/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 빈 Subject 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", "");
        model.addAttribute("code", "");
        model.addAttribute("name", "");
        model.addAttribute("credits", "");
        model.addAttribute("department", "");
        model.addAttribute("professorId", "");
        model.addAttribute("isNew", true);

        // 교수 목록 추가
        model.addAttribute("professors", professorService.getAllProfessors());

        return "subjects/form";
    }

    @PostMapping
    public String saveSubject(@ModelAttribute Subject subject, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        subjectService.saveSubject(subject);
        return "redirect:/subjects";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Subject subject = subjectService.getSubjectById(id);

        // Subject 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", subject.getId());
        model.addAttribute("code", subject.getCode());
        model.addAttribute("name", subject.getName());
        model.addAttribute("credits", subject.getCredits());
        model.addAttribute("department", subject.getDepartment());
        model.addAttribute("professorId", subject.getProfessorId());
        model.addAttribute("isNew", false);

        // 교수 목록 추가
        model.addAttribute("professors", professorService.getAllProfessors());

        return "subjects/form";
    }

    @PostMapping("/{id}")
    public String updateSubject(@PathVariable Long id,
                                @ModelAttribute Subject subject,
                                HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        subjectService.updateSubject(id, subject);
        return "redirect:/subjects";
    }

    @GetMapping("/{id}/delete")
    public String deleteSubject(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        subjectService.deleteSubject(id);
        return "redirect:/subjects";
    }
}