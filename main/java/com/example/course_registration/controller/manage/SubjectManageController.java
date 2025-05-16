package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Subject;
import com.example.course_registration.repository.SubjectRepository;
import com.example.course_registration.repository.DepartmentRepository;
import com.example.course_registration.repository.ProfessorRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/subjects")
public class SubjectManageController {

    private final SubjectRepository subjRepo;
    private final DepartmentRepository deptRepo;
    private final ProfessorRepository profRepo;

    public SubjectManageController(
            SubjectRepository subjRepo,
            DepartmentRepository deptRepo,
            ProfessorRepository profRepo) {
        this.subjRepo = subjRepo;
        this.deptRepo = deptRepo;
        this.profRepo = profRepo;
    }

    @GetMapping
    public String list(Model model,
                       @RequestParam(value="deptId", required=false) Long deptId,
                       @RequestParam(value="profId", required=false) Long profId,
                       @RequestParam(value="semester", required=false) String semester) {
        List<Subject> list = subjRepo.findAll();
        if(deptId != null)   list = subjRepo.findByDepartmentId(deptId);
        else if(profId != null) list = subjRepo.findByProfessorId(profId);
        else if(semester != null && !semester.isBlank())
            list = subjRepo.findBySemester(semester);

        model.addAttribute("subjects", list);
        model.addAttribute("departments", deptRepo.findAll());
        model.addAttribute("professors", profRepo.findAll());
        model.addAttribute("selectedDept", deptId);
        model.addAttribute("selectedProf", profId);
        model.addAttribute("selectedSemester", semester);
        return "manage/subjects";
    }

    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("subject", new Subject());
        model.addAttribute("departments", deptRepo.findAll());
        model.addAttribute("professors", profRepo.findAll());
        return "manage/subject_form";
    }

    @PostMapping("/add")
    public String addSubmit(Subject subject) {
        subjRepo.save(subject);
        return "redirect:/admin/subjects";
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        Subject s = subjRepo.findById(id).orElseThrow();
        model.addAttribute("subject", s);
        model.addAttribute("departments", deptRepo.findAll());
        model.addAttribute("professors", profRepo.findAll());
        return "manage/subject_form";
    }

    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id, Subject subject) {
        subject.setId(id);
        subjRepo.save(subject);
        return "redirect:/admin/subjects";
    }

    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        subjRepo.deleteById(id);
        return "redirect:/admin/subjects";
    }
}
