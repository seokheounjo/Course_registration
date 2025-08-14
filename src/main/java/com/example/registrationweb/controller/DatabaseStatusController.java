package com.example.registrationweb.controller;

import com.example.registrationweb.service.DatabaseStatusService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/admin/database")
public class DatabaseStatusController {

    private final DatabaseStatusService databaseStatusService;

    public DatabaseStatusController(DatabaseStatusService databaseStatusService) {
        this.databaseStatusService = databaseStatusService;
    }

    @GetMapping("/status")
    public String databaseStatus(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        model.addAttribute("dbStatus", databaseStatusService.getDatabaseStatus());
        return "admin/database-status";
    }
}