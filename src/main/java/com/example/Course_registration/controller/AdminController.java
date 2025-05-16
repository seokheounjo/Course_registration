package com.example.Course_registration.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/admin")
public class AdminController {

    @GetMapping("/home")
    public String adminHome(Model model) {
        model.addAttribute("message", "관리자입니다.");
        return "admin_home";
    }
}
