package com.example.course_registration.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/student")
public class StudentController {

    @GetMapping("/home")
    public String studentHome(Model model) {
        model.addAttribute("message", "학생입니다.");
        return "student_home";
    }
}
