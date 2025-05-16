package com.example.course_registration.controller.manage;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
@RequestMapping("/admin")
public class ManageHomeController {

    @GetMapping("/home")
    public String home(Model model) {
        // 메뉴명과 실제 매핑 경로를 함께 넘김
        model.addAttribute("menuItems", List.of(
                new MenuItem("학과 관리", "departments"),
                new MenuItem("교수 관리", "professors"),
                new MenuItem("학생 관리", "students"),
                new MenuItem("강의실 관리", "rooms"),
                new MenuItem("과목 관리", "subjects"),
                new MenuItem("시간표 관리", "schedules")
        ));
        return "manage/manage_home";
    }

    // 내부 정적 클래스: 메뉴 항목
    public static class MenuItem {
        private final String label;
        private final String path;
        public MenuItem(String label, String path) {
            this.label = label;
            this.path = path;
        }
        public String getLabel() { return label; }
        public String getPath() { return path; }
    }
}
