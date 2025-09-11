package com.example.registrationweb.controller;

import com.example.registrationweb.model.Student;
import com.example.registrationweb.service.StudentService;
import jakarta.servlet.http.HttpSession;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/admin/students")
public class AdminStudentController {

    private final StudentService studentService;

    public AdminStudentController(StudentService studentService) {
        this.studentService = studentService;
    }

    @GetMapping
    public String listStudents(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir,
            @RequestParam(required = false) String grade,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String studentId,
            Model model, HttpSession session) {
        
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Page<Student> studentsPage;
        
        // 검색 조건이 있는 경우
        if ((grade != null && !grade.trim().isEmpty()) ||
            (name != null && !name.trim().isEmpty()) ||
            (studentId != null && !studentId.trim().isEmpty())) {
            studentsPage = studentService.searchStudents(grade, name, studentId, page, size, sortBy, sortDir);
        } else {
            studentsPage = studentService.getAllStudents(page, size, sortBy, sortDir);
        }
        
        model.addAttribute("studentsPage", studentsPage);
        model.addAttribute("students", studentsPage.getContent());
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", studentsPage.getTotalPages());
        model.addAttribute("totalItems", studentsPage.getTotalElements());
        model.addAttribute("size", size);
        model.addAttribute("sortBy", sortBy);
        model.addAttribute("sortDir", sortDir);
        model.addAttribute("reverseSortDir", sortDir.equals("asc") ? "desc" : "asc");
        
        // 검색 파라미터 유지
        model.addAttribute("searchGrade", grade);
        model.addAttribute("searchName", name);
        model.addAttribute("searchStudentId", studentId);
        
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
        model.addAttribute("email", "");
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
        model.addAttribute("email", student.getEmail());
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