// controller: /student/enrollments 수강 내역 페이지
package com.example.Course_registration.controller.student;

import com.example.Course_registration.Service.student.EnrollmentService;
import com.example.Course_registration.repository.student.EnrollmentRepository;
import com.example.Course_registration.repository.student.SubjectRepository;
import com.example.Course_registration.entity.student.Enrollment;
import com.example.Course_registration.entity.student.Subject;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.*;

@Controller
public class EnrollmentViewController {

    @Autowired
    private EnrollmentRepository enrollmentRepository;

    @Autowired
    private SubjectRepository subjectRepository;

    @Autowired
    private EnrollmentService enrollmentService;

    // 수강 신청
    @PostMapping("/enroll")
    public String enroll(@RequestParam("subjectId") Long subjectId,
                         HttpSession session,
                         RedirectAttributes redirectAttributes) {
        Long studentId = (Long) session.getAttribute("studentId");
        if (studentId == null) {
            redirectAttributes.addFlashAttribute("message", "로그인이 필요합니다.");
            return "redirect:/login";
        }
        String resultMessage = enrollmentService.enrollStudent(studentId, subjectId);
        redirectAttributes.addFlashAttribute("message", resultMessage);
        return "redirect:/student/subjects";
    }

    // 수강 취소
    @PostMapping("/enroll/cancel")
    public String cancel(@RequestParam("subjectId") Long subjectId,
                         HttpSession session,
                         RedirectAttributes redirectAttributes) {
        Long studentId = (Long) session.getAttribute("studentId");
        if (studentId == null) {
            redirectAttributes.addFlashAttribute("message", "로그인이 필요합니다.");
            return "redirect:/login";
        }
        enrollmentService.cancelEnrollment(studentId, subjectId);
        redirectAttributes.addFlashAttribute("message", "수강 신청이 취소되었습니다.");
        return "redirect:/student/enrollments";
    }

    @GetMapping("/student/enrollments")
    public String viewEnrollments(Model model, HttpSession session) {
        Long studentId = (Long) session.getAttribute("studentId");
        if (studentId == null) {
            return "redirect:/login";
        }

        List<Enrollment> enrollments = enrollmentRepository.findByStudentId(studentId);
        Map<Subject, String> subjectInfo = new LinkedHashMap<>();

        for (Enrollment e : enrollments) {
            subjectRepository.findById(e.getSubjectId()).ifPresent(subject -> {
                subjectInfo.put(subject, e.getEnrolledAt().toString());
            });
        }

        model.addAttribute("subjectInfo", subjectInfo);
        return "student/student_enrollments";
    }
}
