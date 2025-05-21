package com.example.registrationweb.controller;

import com.example.registrationweb.model.Student;
import com.example.registrationweb.service.StudentService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class LoginController {

    private final StudentService studentService;

    public LoginController(StudentService studentService) {
        this.studentService = studentService;
    }

    @GetMapping("/")
    public String showLoginForm() {
        return "login";
    }

    // GET 요청으로 /login 들어오는 경우도 처리
    @GetMapping("/login")
    public String getLoginForm() {
        return "login";
    }

    @PostMapping("/login")
    public String login(@RequestParam String username,
                        @RequestParam String password,
                        HttpSession session,
                        Model model) {
        // 관리자 로그인 확인
        if ("admin01".equals(username) && "admin01".equals(password)) {
            session.setAttribute("user", "admin");
            session.setAttribute("username", username);
            return "redirect:/admin";
        }
        // 학생 로그인 확인
        else {
            Student student = studentService.validateStudent(username, password);
            if (student != null) {
                session.setAttribute("user", "student");
                session.setAttribute("username", username);
                session.setAttribute("studentId", student.getId());
                return "redirect:/student";
            } else {
                model.addAttribute("error", "ID 또는 PW가 올바르지 않습니다.");
                return "login";
            }
        }
    }

    @GetMapping("/admin")
    public String adminPage(HttpSession session) {
        // 관리자 로그인 확인
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }
        return "admin";
    }

    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}
