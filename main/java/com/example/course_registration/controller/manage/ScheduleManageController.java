package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.SubjectSchedule;
import com.example.course_registration.repository.SubjectScheduleRepository;
import com.example.course_registration.repository.SubjectRepository;
import com.example.course_registration.repository.RoomRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin/schedules")
public class ScheduleManageController {

    private final SubjectScheduleRepository schRepo;
    private final SubjectRepository subjRepo;
    private final RoomRepository roomRepo;

    public ScheduleManageController(SubjectScheduleRepository schRepo,
                                    SubjectRepository subjRepo,
                                    RoomRepository roomRepo) {
        this.schRepo = schRepo;
        this.subjRepo = subjRepo;
        this.roomRepo = roomRepo;
    }

    @GetMapping
    public String list(Model model,
                       @RequestParam(value="subjectId", required=false) Long subjectId) {
        List<SubjectSchedule> list = (subjectId == null)
                ? schRepo.findAll()
                : schRepo.findBySubjectId(subjectId);
        model.addAttribute("schedules", list);
        model.addAttribute("subjects", subjRepo.findAll());
        model.addAttribute("selectedSubj", subjectId);
        return "manage/schedules";
    }

    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("schedule", new SubjectSchedule());
        model.addAttribute("subjects", subjRepo.findAll());
        model.addAttribute("rooms", roomRepo.findAll());
        return "manage/schedule_form";
    }

    @PostMapping("/add")
    public String addSubmit(SubjectSchedule schedule) {
        schRepo.save(schedule);
        return "redirect:/admin/schedules";
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        SubjectSchedule s = schRepo.findById(id).orElseThrow();
        model.addAttribute("schedule", s);
        model.addAttribute("subjects", subjRepo.findAll());
        model.addAttribute("rooms", roomRepo.findAll());
        return "manage/schedule_form";
    }

    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id,
                             SubjectSchedule schedule) {
        schedule.setId(id);
        schRepo.save(schedule);
        return "redirect:/admin/schedules";
    }

    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        schRepo.deleteById(id);
        return "redirect:/admin/schedules";
    }
}
