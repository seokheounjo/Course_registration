// controller 수정: 신청된 과목은 신청 완료로 구분
package com.example.Course_registration.controller.student;

import com.example.Course_registration.repository.student.EnrollmentRepository;
import com.example.Course_registration.repository.student.SubjectRepository;
import com.example.Course_registration.entity.student.Subject;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.*;

@Controller
public class SubjectController {

    @Autowired
    private SubjectRepository subjectRepository;

    @Autowired
    private EnrollmentRepository enrollmentRepository;

    @GetMapping("/student/subjects")
    public String showSubjects(Model model, HttpSession session) {
        Long studentId = (Long) session.getAttribute("studentId");
        if (studentId == null) {
            return "redirect:/login";
        }

        List<Subject> subjectList = subjectRepository.findAll();
        List<Long> enrolledIds = enrollmentRepository.findSubjectIdsByStudentId(studentId);

        // Subject별로 신청여부를 체크하는 Map 구성
        Map<Long, Boolean> enrolledMap = new HashMap<>();
        for (Subject s : subjectList) {
            enrolledMap.put(s.getId(), enrolledIds.contains(s.getId()));
        }

        model.addAttribute("subjects", subjectList);
        model.addAttribute("enrolledMap", enrolledMap);
        return "student/student_subjects";
    }
}
