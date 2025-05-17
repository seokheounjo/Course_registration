package com.example.Course_registration.service.admin;

import com.example.Course_registration.entity.SubjectSchedule;
import com.example.Course_registration.repository.SubjectRepository;
import com.example.Course_registration.repository.RoomRepository;
import com.example.Course_registration.service.admin
        .AdminScheduleService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/admin/schedules")
@RequiredArgsConstructor
public class AdminScheduleController {

    private final AdminScheduleService scheduleService;
    private final SubjectRepository subjectRepository;
    private final RoomRepository roomRepository;

    // 목록
    @GetMapping
    public String list(Model model) {
        model.addAttribute("schedules", scheduleService.findAll());
        return "admin/schedule/list";
    }

    // 등록 폼
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("schedule", new SubjectSchedule());
        model.addAttribute("subjects", subjectRepository.findAll());
        model.addAttribute("rooms", roomRepository.findAll());
        return "admin/schedule/form";
    }

    // 등록 처리
    @PostMapping
    public String create(@ModelAttribute SubjectSchedule schedule) {
        scheduleService.save(schedule);
        return "redirect:/admin/schedules";
    }

    // 수정 폼
    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("schedule", scheduleService.findById(id));
        model.addAttribute("subjects", subjectRepository.findAll());
        model.addAttribute("rooms", roomRepository.findAll());
        return "admin/schedule/form";
    }

    // 수정 처리
    @PostMapping("/{id}/edit")
    public String update(@ModelAttribute SubjectSchedule schedule) {
        scheduleService.save(schedule);
        return "redirect:/admin/schedules";
    }

    // 삭제 처리
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        scheduleService.delete(id);
        return "redirect:/admin/schedules";
    }
}
