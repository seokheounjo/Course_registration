package com.example.Course_registration.controller.admin;

import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.entity.SubjectSchedule;
import com.example.Course_registration.repository.DepartmentRepository;
import com.example.Course_registration.repository.ProfessorRepository;
import com.example.Course_registration.repository.SubjectRepository;
import com.example.Course_registration.repository.SubjectScheduleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalTime;

@Controller
@RequiredArgsConstructor
public class AdminDashboardController {

    private final ProfessorRepository professorRepo;
    private final SubjectRepository subjectRepo;
    private final SubjectScheduleRepository scheduleRepo;
    private final DepartmentRepository departmentRepo;

    @GetMapping("/admin/dashboard")
    public String dashboard() {
        return "admin_dashboard";
    }

    @GetMapping("/admin/new")
    public String newForm(Model model) {
        model.addAttribute("departments", departmentRepo.findAll());
        return "admin_new";
    }

    @PostMapping("/admin/new")
    public String createAll(@RequestParam String professorName,
                            @RequestParam String professorEmail,
                            @RequestParam String professorPassword,
                            @RequestParam String subjectName,
                            @RequestParam Integer credits,
                            @RequestParam Integer capacity,
                            @RequestParam String semester,
                            @RequestParam Long departmentId,
                            @RequestParam String dayOfWeek,
                            @RequestParam String startTime,
                            @RequestParam String endTime) {

        LocalTime parsedStart = LocalTime.parse(startTime);
        LocalTime parsedEnd = LocalTime.parse(endTime);

        // 1. 교수 저장
        Professor prof = new Professor();
        prof.setName(professorName);
        prof.setEmail(professorEmail);
        prof.setPassword(professorPassword);
        professorRepo.save(prof);

        // 2. 과목 저장
        Department dept = departmentRepo.findById(departmentId).orElseThrow();
        Subject subject = new Subject();
        subject.setName(subjectName);
        subject.setCredits(credits);
        subject.setCapacity(capacity);
        subject.setSemester(semester);
        subject.setDepartment(dept);
        subject.setProfessor(prof);
        subjectRepo.save(subject);

        // 3. 시간표 저장
        SubjectSchedule schedule = new SubjectSchedule();
        schedule.setDayOfWeek(dayOfWeek);
        schedule.setStartTime(parsedStart);
        schedule.setEndTime(parsedEnd);
        schedule.setSubject(subject);
        scheduleRepo.save(schedule);

        return "redirect:/admin/dashboard";
    }
}
