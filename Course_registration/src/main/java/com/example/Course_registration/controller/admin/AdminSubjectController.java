package com.example.Course_registration.controller.admin;

import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.entity.SubjectSchedule;
import com.example.Course_registration.repository.RoomRepository;
import com.example.Course_registration.repository.SubjectRepository;
import com.example.Course_registration.repository.DepartmentRepository;
import com.example.Course_registration.repository.ProfessorRepository;
import com.example.Course_registration.service.admin.AdminSubjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/subjects")
@RequiredArgsConstructor
public class AdminSubjectController {

    private final AdminSubjectService subjectService;
    private final SubjectRepository subjectRepository;
    private final DepartmentRepository departmentRepository;
    private final ProfessorRepository professorRepository;
    private final RoomRepository roomRepository;

    @GetMapping
    public String list(Model model) {
        List<Subject> subjects = subjectRepository.findAll();
        model.addAttribute("subjects", subjects);
        model.addAttribute("professors", professorRepository.findAll());
        model.addAttribute("departments", departmentRepository.findAll());
        model.addAttribute("grade", "");
        return "admin/subject/list";
    }

    @GetMapping("/unassigned")
    public String unassignedSubjects(Model model) {
        model.addAttribute("subjects", subjectRepository.findByProfessorIsNull());
        return "admin/subject/unassigned";
    }

    // ✅ 과목 등록 폼
    /** 과목 등록 폼 */
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("subject", new Subject());           // ✅ 반드시 존재
        model.addAttribute("professors", professorRepository.findAll());
        model.addAttribute("departments", departmentRepository.findAll());
        return "admin/subject/form";
    }

    // ✅ 과목 등록 처리
    @PostMapping
    public String create(@ModelAttribute Subject subject, Model model) {
        if (subject.getProfessor() == null) {
            model.addAttribute("message", "⚠️ 담당 교수가 없습니다. 이후에 배정 가능합니다.");
            model.addAttribute("subject", subject);
            model.addAttribute("professors", professorRepository.findAll());
            model.addAttribute("departments", departmentRepository.findAll());
            return "admin/subject/form";
        }
        subjectService.save(subject);
        return "redirect:/admin/subjects";
    }

    // ✅ 과목 수정 폼
    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        Subject subject = subjectService.findById(id);

        Long selectedProfessorId = subject.getProfessor() != null ? subject.getProfessor().getId() : null;
        Long selectedDepartmentId = subject.getDepartment().getId();

        List<Professor> professors = professorRepository.findAll();
        List<Department> departments = departmentRepository.findAll();

        professors.forEach(p -> {
            if (selectedProfessorId != null && p.getId().equals(selectedProfessorId)) {
                p.setSelected(true);
            }
        });

        departments.forEach(d -> {
            if (d.getId().equals(selectedDepartmentId)) {
                d.setSelected(true);
            }
        });

        SubjectSchedule dummySchedule = new SubjectSchedule();
        dummySchedule.setDayOfWeek("");  // null 방지

        model.addAttribute("subject", subject);
        model.addAttribute("schedule", dummySchedule);  // ← Mustache에서 시간표 입력용
        model.addAttribute("professors", professors);
        model.addAttribute("departments", departments);
        model.addAttribute("rooms", roomRepository.findAll());
        model.addAttribute("subjects", subjectRepository.findAll());

        return "admin/subject/form";
    }

    @PostMapping("/{id}/edit")
    public String update(@ModelAttribute Subject subject) {
        subjectService.save(subject);
        return "redirect:/admin/subjects";
    }

    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        subjectService.delete(id);
        return "redirect:/admin/subjects";
    }

    @GetMapping("/search")
    public String searchSubjects(
            @RequestParam(required = false) Long professorId,
            @RequestParam(required = false) Long departmentId,
            @RequestParam(required = false) String grade,
            Model model
    ) {
        List<Subject> subjects = subjectService.searchSubjects(professorId, departmentId, grade);

        List<Professor> professors = professorRepository.findAll();
        List<Department> departments = departmentRepository.findAll();

        professors.forEach(p -> {
            if (professorId != null && p.getId().equals(professorId)) {
                p.setSelected(true);
            }
        });

        departments.forEach(d -> {
            if (departmentId != null && d.getId().equals(departmentId)) {
                d.setSelected(true);
            }
        });

        model.addAttribute("subjects", subjects);
        model.addAttribute("professors", professors);
        model.addAttribute("departments", departments);
        model.addAttribute("grade", grade);
        return "admin/subject/list";
    }
}
