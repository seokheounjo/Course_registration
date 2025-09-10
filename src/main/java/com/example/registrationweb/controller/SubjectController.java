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

    @PostMapping("/bulk")
    @ResponseBody
    public String bulkAddSubjects(HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "Access denied";
        }

        try {
            // 4학년 과목들을 직접 코드로 추가
            String[][] subjects = {
                {"컴퓨401", "고급알고리즘", "3", "컴퓨터공학과", "1", "4"},
                {"컴퓨402", "머신러닝", "3", "컴퓨터공학과", "21", "4"},
                {"컴퓨403", "네트워크보안", "3", "컴퓨터공학과", "31", "4"},
                {"전자401", "임베디드시스템", "3", "전자공학과", "2", "4"},
                {"전자402", "VLSI설계", "3", "전자공학과", "22", "4"},
                {"전자403", "신호처리응용", "3", "전자공학과", "32", "4"},
                {"기계401", "로봇공학", "3", "기계공학과", "3", "4"},
                {"기계402", "제어시스템설계", "3", "기계공학과", "23", "4"},
                {"기계403", "유체역학응용", "3", "기계공학과", "33", "4"},
                {"경영401", "전략경영", "3", "경영학과", "4", "4"},
                {"경영402", "국제경영", "3", "경영학과", "24", "4"},
                {"경영403", "경영정보시스템", "3", "경영학과", "34", "4"},
                {"화학401", "고분자화학", "3", "화학공학과", "5", "4"},
                {"화학402", "반응공학", "3", "화학공학과", "25", "4"},
                {"화학403", "분리정제공학", "3", "화학공학과", "35", "4"},
                {"생명401", "분자생물학", "3", "생명과학과", "6", "4"},
                {"생명402", "생명정보학", "3", "생명과학과", "26", "4"},
                {"생명403", "유전공학", "3", "생명과학과", "36", "4"},
                {"수학401", "수치해석", "3", "수학과", "7", "4"},
                {"수학402", "편미분방정식", "3", "수학과", "27", "4"}
            };

            int added = 0;
            for (String[] subjectData : subjects) {
                Subject subject = new Subject();
                subject.setCode(subjectData[0]);
                subject.setName(subjectData[1]);
                subject.setCredits(Integer.parseInt(subjectData[2]));
                subject.setDepartment(subjectData[3]);
                // Professor ID로 Professor 객체를 찾아서 설정
                Long professorId = Long.parseLong(subjectData[4]);
                subject.setProfessor(professorService.getProfessorById(professorId));
                subject.setTargetGrade(subjectData[5]);
                
                subjectService.saveSubject(subject);
                added++;
            }
            
            return "Success: Added " + added + " subjects for 4th year students";
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
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