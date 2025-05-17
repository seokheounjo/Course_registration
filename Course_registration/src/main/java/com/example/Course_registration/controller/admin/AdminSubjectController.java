package com.example.Course_registration.controller.admin;

import com.example.Course_registration.dto.SubjectForm;
import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
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

    private final AdminSubjectService  subjectService;
    private final ProfessorRepository  professorRepo;
    private final DepartmentRepository departmentRepo;

    /* ───── 목록 ───── */
    @GetMapping
    public String list(Model model) {
        model.addAttribute("subjects"   , subjectService.findAll());
        return "admin/subject/list";
    }

    /* ───── 신규 폼 ───── */
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("form", new SubjectForm());      // ← 이름을 form 으로 고정
        loadCombo(model, null, null);
        return "admin/subject/form";
    }

    /* ───── 신규 저장 ───── */
    @PostMapping
    public String create(@ModelAttribute("form") SubjectForm form, Model model) {

        /* 필수 체크 */
        if (form.getDepartmentId() == null) {
            model.addAttribute("message", "⚠️ 소속학과는 필수입니다.");
            loadCombo(model, form.getProfessorId(), null);
            return "admin/subject/form";
        }

        Department dept = departmentRepo.findById(form.getDepartmentId()).orElseThrow();
        Professor  prof = (form.getProfessorId() != null)
                ? professorRepo.findById(form.getProfessorId()).orElse(null)
                : null;

        subjectService.save(form.toEntity(prof, dept));
        return "redirect:/admin/subjects";
    }

    /* ───── 수정 폼 ───── */
    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        Subject      s  = subjectService.findById(id);
        SubjectForm  df = new SubjectForm(s);               // DTO 로 변환

        Long selProf = (s.getProfessor()  != null) ? s.getProfessor().getId()  : null;
        Long selDept = (s.getDepartment() != null) ? s.getDepartment().getId() : null;

        model.addAttribute("form", df);
        loadCombo(model, selProf, selDept);
        return "admin/subject/form";
    }

    /* ───── 수정 저장 ───── */
    @PostMapping("/{id}/edit")
    public String update(@PathVariable Long id,
                         @ModelAttribute("form") SubjectForm form) {

        Department dept = departmentRepo.findById(form.getDepartmentId()).orElseThrow();
        Professor  prof = (form.getProfessorId() != null)
                ? professorRepo.findById(form.getProfessorId()).orElse(null)
                : null;

        form.setId(id);                    // 식별자 주입
        subjectService.save(form.toEntity(prof, dept));
        return "redirect:/admin/subjects";
    }

    /* ───── 삭제 ───── */
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        subjectService.delete(id);
        return "redirect:/admin/subjects";
    }

    /* ── 드롭다운 공통 로직 ── */
    private void loadCombo(Model model, Long selProfId, Long selDeptId) {
        List<Professor>  professors  = professorRepo.findAll();
        List<Department> departments = departmentRepo.findAll();

        professors .forEach(p -> p.setSelected(selProfId  != null && p.getId().equals(selProfId)));
        departments.forEach(d -> d.setSelected(selDeptId != null && d.getId().equals(selDeptId)));

        model.addAttribute("professors" , professors);
        model.addAttribute("departments", departments);
    }
}
