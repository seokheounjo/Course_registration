package com.example.registrationweb.controller;

import com.example.registrationweb.model.Student;
import com.example.registrationweb.service.StudentService;
import com.example.registrationweb.service.DatabaseStatusService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/admin/students")
public class AdminStudentController {

    private final StudentService studentService;
    private final DatabaseStatusService databaseStatusService;

    public AdminStudentController(StudentService studentService, DatabaseStatusService databaseStatusService) {
        this.studentService = studentService;
        this.databaseStatusService = databaseStatusService;
    }

    @GetMapping
    public String listStudents(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("students", studentService.getAllStudents());
        model.addAttribute("dbStatus", databaseStatusService.getDatabaseStatus());
        return "admin/students/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 빈 Student 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", "");
        model.addAttribute("studentId", "");
        model.addAttribute("name", "");
        model.addAttribute("department", "");
        model.addAttribute("password", "");
        model.addAttribute("grade", "");
        model.addAttribute("isNew", true);

        return "admin/students/form";
    }

    @PostMapping
    public String saveStudent(@ModelAttribute Student student, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        studentService.saveStudent(student);
        return "redirect:/admin/students";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Student student = studentService.getStudentById(id);
        if (student == null) {
            return "redirect:/admin/students";
        }

        // Student 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", student.getId());
        model.addAttribute("studentId", student.getStudentId());
        model.addAttribute("name", student.getName());
        model.addAttribute("department", student.getDepartment());
        model.addAttribute("password", student.getPassword());
        model.addAttribute("grade", student.getGrade());
        model.addAttribute("isNew", false);

        return "admin/students/form";
    }

    @PostMapping("/{id}")
    public String updateStudent(@PathVariable Long id,
                                @ModelAttribute Student student,
                                HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        studentService.updateStudent(id, student);
        return "redirect:/admin/students";
    }

    @GetMapping("/{id}/delete")
    public String deleteStudent(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        studentService.deleteStudent(id);
        return "redirect:/admin/students";
    }
}