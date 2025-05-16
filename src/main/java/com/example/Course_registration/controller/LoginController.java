package com.example.Course_registration.controller;

import com.example.Course_registration.entity.Student;  // ✅ 이걸로 되어 있어야 함
import jakarta.servlet.http.HttpSession;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import com.example.Course_registration.entity.Admin;

@Controller
public class LoginController {

    @GetMapping("/login")
    public String loginForm(@RequestParam(value = "error", required = false) String error,
                            @RequestParam(value = "logout", required = false) String logout,
                            Model model) {
        if (error != null) {
            model.addAttribute("error", true);
        }
        if (logout != null) {
            model.addAttribute("logout", true);
        }
        return "login";
    }

    @GetMapping("/route")
    public String routeAfterLogin(Authentication authentication, HttpSession session) {
        String role = authentication.getAuthorities()
                .iterator()
                .next()
                .getAuthority();

        Object principal = authentication.getPrincipal();
        System.out.println("AUTH PRINCIPAL TYPE = " + principal.getClass().getName());

        if ("ROLE_ADMIN".equals(role)) {
            if (principal instanceof Admin admin) {
                session.setAttribute("adminId", admin.getId());
                System.out.println("✔ 세션에 adminId 저장됨: " + admin.getId());
            } else {
                System.out.println("❌ Admin 타입 아님: " + principal);
            }
            return "redirect:/admin/home";

        } else if ("ROLE_STUDENT".equals(role)) {
            if (principal instanceof Student student) {
                session.setAttribute("studentId", student.getId());
                System.out.println("✔ 세션에 studentId 저장됨: " + student.getId());
            } else {
                System.out.println("❌ Student 타입 아님: " + principal);
            }
            return "redirect:/student/home";
        }

//        else if ("ROLE_PROFESSOR".equals(role)) {
//            if (principal instanceof Professor professor) {
//                session.setAttribute("professorId", professor.getId());
//            }
//            return "redirect:/professor/home";
//        }

        return "redirect:/login";
    }
}
