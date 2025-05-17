package com.example.Course_registration.controller.admin;

import com.example.Course_registration.dto.SubjectForm;
import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.repository.DepartmentRepository;
import com.example.Course_registration.repository.ProfessorRepository;
import com.example.Course_registration.repository.SubjectRepository;
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

    private final AdminSubjectService  subjectService;
    private final SubjectRepository    subjectRepo;
    private final ProfessorRepository  professorRepo;
    private final DepartmentRepository departmentRepo;

    /* ----------------------------- 목록 ----------------------------- */
    @GetMapping
    public String list(Model model) {

        model.addAttribute("subjects"   , subjectRepo.findAll());
        model.addAttribute("professors" , professorRepo.findAll());
        model.addAttribute("departments", departmentRepo.findAll());
        model.addAttribute("grade"      , "");                 // 검색창 초기값

        return "admin/subject/list";
    }

    /* ---------------------------- 신규 폼 ---------------------------- */
    @GetMapping("/new")
    public String newForm(Model model) {

        model.addAttribute("subject"    , new Subject());      // ① 주인 객체
        model.addAttribute("professors" , professorRepo.findAll());
        model.addAttribute("departments", departmentRepo.findAll());

        return "admin/subject/form";
    }

    /* ---------------------------- 신규 저장 --------------------------- */
    @PostMapping
    public String create(@ModelAttribute("form") SubjectForm form,
                         Model model) {

        // 필수 값 체크
        if (form.getDepartmentId() == null) {
            model.addAttribute("message"   , "⚠️ 소속학과는 필수입니다.");
            model.addAttribute("subject"   , new Subject());
            model.addAttribute("professors", professorRepo.findAll());
            model.addAttribute("departments", departmentRepo.findAll());
            return "admin/subject/form";
        }

        Department dept = departmentRepo.findById(form.getDepartmentId()).orElse(null);
        Professor  prof = (form.getProfessorId() != null)
                ? professorRepo.findById(form.getProfessorId()).orElse(null)
                : null;

        subjectService.save(form.toEntity(prof, dept));
        return "redirect:/admin/subjects";
    }

    /* ----------------------------- 수정 폼 ---------------------------- */
    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {

        Subject subject = subjectService.findById(id);

        List<Professor>  professors  = professorRepo.findAll();
        List<Department> departments = departmentRepo.findAll();

        professors.forEach(p ->
                p.setSelected(subject.getProfessor() != null &&
                        p.getId().equals(subject.getProfessor().getId())));

        departments.forEach(d ->
                d.setSelected(d.getId().equals(subject.getDepartment().getId())));

        model.addAttribute("subject"    , subject);
        model.addAttribute("professors" , professors);
        model.addAttribute("departments", departments);

        return "admin/subject/form";
    }

    /* ----------------------------- 수정 저장 -------------------------- */
    @PostMapping("/{id}/edit")
    public String update(@PathVariable Long id,
                         @ModelAttribute("form") SubjectForm form) {

        Department dept = departmentRepo.findById(form.getDepartmentId()).orElse(null);
        Professor  prof = (form.getProfessorId() != null)
                ? professorRepo.findById(form.getProfessorId()).orElse(null)
                : null;

        form.setId(id);                                 // DTO 에 id 주입
        subjectService.save(form.toEntity(prof, dept));

        return "redirect:/admin/subjects";
    }

    /* ----------------------------- 삭제 ------------------------------ */
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        subjectService.delete(id);
        return "redirect:/admin/subjects";
    }

    /* ----------------------------- 검색 ------------------------------ */
    @GetMapping("/search")
    public String search(@RequestParam(required = false) Long professorId,
                         @RequestParam(required = false) Long departmentId,
                         @RequestParam(required = false) String grade,
                         Model model) {

        model.addAttribute("subjects",
                subjectService.searchSubjects(professorId, departmentId, grade));

        /* ✔ 선택값 유지 */
        List<Professor>  profs = professorRepo.findAll();
        List<Department> depts = departmentRepo.findAll();

        profs.forEach(p -> p.setSelected(professorId  != null &&
                p.getId().equals(professorId)));
        depts.forEach(d -> d.setSelected(departmentId != null &&
                d.getId().equals(departmentId)));

        model.addAttribute("professors" , profs);
        model.addAttribute("departments", depts);
        model.addAttribute("grade"      , grade);

        return "admin/subject/list";
    }
}
