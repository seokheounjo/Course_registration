package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Department;
import com.example.course_registration.entity.Subject;
import com.example.course_registration.repository.DepartmentRepository;
import com.example.course_registration.repository.SubjectRepository;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/subjects")
public class SubjectManageController {

    private final SubjectRepository subjectRepo;
    private final DepartmentRepository deptRepo;

    public SubjectManageController(SubjectRepository subjectRepo,
                                   DepartmentRepository deptRepo) {
        this.subjectRepo = subjectRepo;
        this.deptRepo = deptRepo;
    }

    // 과목 목록 & 검색
    @GetMapping
    public String list(Model model,
                       @RequestParam(value="keyword", required=false) String keyword) {
        String kw = (keyword == null ? "" : keyword.trim());
        List<Subject> list = kw.isEmpty()
                ? subjectRepo.findAll()
                : subjectRepo.findByNameContaining(kw); // 이 메서드가 실제로 존재해야 함
        model.addAttribute("subjects", list);
        model.addAttribute("keyword", kw);
        return "manage/subjects"; // 정확한 뷰 경로 지정
    }

    // 과목 등록 폼
    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("subject", new Subject());
        model.addAttribute("departments", deptRepo.findAll());
        return "manage/subject_form";
    }

    // 과목 등록 처리
    @PostMapping("/add")
    public String addSubmit(@ModelAttribute Subject subject,
                            @RequestParam Long departmentId) {
        Department dept = deptRepo.findById(departmentId).orElseThrow();
        subject.setDepartment(dept);
        subjectRepo.save(subject);
        return "redirect:/admin/subjects"; // 저장 후 리디렉션
    }

    // 과목 수정 폼
    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        Subject subject = subjectRepo.findById(id).orElseThrow();
        model.addAttribute("subject", subject);
        model.addAttribute("departments", deptRepo.findAll());
        return "manage/subject_form";
    }

    // 과목 수정 처리
    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id,
                             @ModelAttribute Subject formData,
                             @RequestParam Long departmentId) {
        Subject subject = subjectRepo.findById(id).orElseThrow();
        subject.setName(formData.getName());
        subject.setCredits(formData.getCredits());
        subject.setCapacity(formData.getCapacity());
        subject.setSemester(formData.getSemester());
        Department dept = deptRepo.findById(departmentId).orElseThrow();
        subject.setDepartment(dept);
        subjectRepo.save(subject);
        return "redirect:/admin/subjects"; // 수정 후 리디렉션
    }

    // 과목 삭제
    @Transactional
    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        subjectRepo.deleteById(id);
        return "redirect:/admin/subjects"; // 삭제 후 리디렉션
    }
}
