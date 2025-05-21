package com.example.registrationweb.controller;

import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.service.ProfessorService;
import com.example.registrationweb.service.SubjectService;
import com.example.registrationweb.service.TimetableService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/timetable")
public class TimetableController {

    private final TimetableService timetableService;
    private final SubjectService subjectService;
    private final ProfessorService professorService;

    public TimetableController(TimetableService timetableService,
                               SubjectService subjectService,
                               ProfessorService professorService) {
        this.timetableService = timetableService;
        this.subjectService = subjectService;
        this.professorService = professorService;
    }

    @GetMapping
    public String listTimetables(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("timetables", timetableService.getAllTimetables());
        return "timetable/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 빈 Timetable 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", "");
        model.addAttribute("subjectId", "");
        model.addAttribute("day", "");
        model.addAttribute("startTime", "");
        model.addAttribute("endTime", "");
        model.addAttribute("room", "");
        model.addAttribute("professorId", "");
        model.addAttribute("isNew", true);

        // 과목 및 교수 목록 추가
        model.addAttribute("subjects", subjectService.getAllSubjects());
        model.addAttribute("professors", professorService.getAllProfessors());

        return "timetable/form";
    }

    @PostMapping
    public String saveTimetable(@ModelAttribute Timetable timetable, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        timetableService.saveTimetable(timetable);
        return "redirect:/timetable";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Timetable timetable = timetableService.getTimetableById(id);

        // Timetable 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", timetable.getId());
        model.addAttribute("subjectId", timetable.getSubjectId());
        model.addAttribute("day", timetable.getDay());
        model.addAttribute("startTime", timetable.getStartTime());
        model.addAttribute("endTime", timetable.getEndTime());
        model.addAttribute("room", timetable.getRoom());
        model.addAttribute("professorId", timetable.getProfessorId());
        model.addAttribute("isNew", false);

        // 과목 및 교수 목록 추가
        model.addAttribute("subjects", subjectService.getAllSubjects());
        model.addAttribute("professors", professorService.getAllProfessors());

        return "timetable/form";
    }

    @PostMapping("/{id}")
    public String updateTimetable(@PathVariable Long id,
                                  @ModelAttribute Timetable timetable,
                                  HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        timetableService.updateTimetable(id, timetable);
        return "redirect:/timetable";
    }

    @GetMapping("/{id}/delete")
    public String deleteTimetable(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        timetableService.deleteTimetable(id);
        return "redirect:/timetable";
    }
}