package com.example.course_registration.controller.login;

import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

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
    public String routeAfterLogin(Authentication authentication) {
        String role = authentication.getAuthorities()
                .iterator()
                .next()
                .getAuthority();
        if ("ROLE_ADMIN".equals(role)) {
            return "redirect:/admin/home";
        } else {
            return "redirect:/student/home";
        }
    }
}
