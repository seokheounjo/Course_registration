package com.example.Course_registration.controller.student;

import com.example.Course_registration.service.student.EnrollmentService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/student")
public class EnrollmentController {

    @Autowired
    private EnrollmentService enrollmentService;

    /**
     * 수강 신청 요청 처리
     * POST /student/enroll?subjectId={id}
     */
    @PostMapping("/enroll")
    public String enroll(
            @RequestParam("subjectId") Long subjectId,
            HttpSession session,
            RedirectAttributes redirectAttributes
    ) {
        // 로그인한 학생 ID 가져오기 (세션 또는 SecurityContext에서)
        Long studentId = (Long) session.getAttribute("studentId");
        if (studentId == null) {
            redirectAttributes.addFlashAttribute("message", "로그인이 필요합니다.");
            return "redirect:/login";
        }

        // 수강신청 처리
        String resultMessage = enrollmentService.enrollStudent(studentId, subjectId);

        // 결과 메시지 저장 후 리다이렉트
        redirectAttributes.addFlashAttribute("message", resultMessage);
        return "redirect:/student/subjects";  // 과목 목록 페이지로 리다이렉트
    }
}
