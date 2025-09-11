package com.example.registrationweb.controller;

import com.example.registrationweb.model.Enrollment;
import com.example.registrationweb.model.Student;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.service.EnrollmentService;
import com.example.registrationweb.service.StudentService;
import com.example.registrationweb.service.TimetableService;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/debug")
public class DebugController {
    
    private final StudentService studentService;
    private final TimetableService timetableService;
    private final EnrollmentService enrollmentService;
    
    public DebugController(StudentService studentService, 
                          TimetableService timetableService,
                          EnrollmentService enrollmentService) {
        this.studentService = studentService;
        this.timetableService = timetableService;
        this.enrollmentService = enrollmentService;
    }
    
    @GetMapping("/data")
    @ResponseBody
    public Map<String, Object> debugData() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 학생 데이터 확인
            Student student = studentService.getStudentByStudentId("20240101");
            if (student != null) {
                result.put("student_found", true);
                result.put("student_name", student.getName());
                result.put("student_id_db", student.getId());
            } else {
                result.put("student_found", false);
            }
            
            // 시간표 데이터 확인 (첫 5개만)
            List<Timetable> timetables = timetableService.getAllTimetables();
            result.put("timetables_count", timetables.size());
            if (!timetables.isEmpty()) {
                Timetable firstTimetable = timetables.get(0);
                Map<String, Object> timetableInfo = new HashMap<>();
                timetableInfo.put("id", firstTimetable.getId());
                timetableInfo.put("subject_name", firstTimetable.getSubjectName());
                timetableInfo.put("day", firstTimetable.getDay());
                timetableInfo.put("has_subject", firstTimetable.getSubject() != null);
                if (firstTimetable.getSubject() != null) {
                    timetableInfo.put("subject_id", firstTimetable.getSubject().getId());
                }
                result.put("first_timetable", timetableInfo);
            }
            
            // 기존 enrollment 데이터 확인
            if (student != null) {
                List<Enrollment> enrollments = enrollmentService.getEnrollmentsByStudentId(student.getId());
                result.put("existing_enrollments_count", enrollments.size());
            }
            
            // 테스트 수강신청 시도
            if (student != null && !timetables.isEmpty()) {
                Timetable testTimetable = timetables.get(0);
                System.out.println("DEBUG TEST: Attempting enrollment - Student: " + student.getId() + ", Timetable: " + testTimetable.getId());
                
                Enrollment testEnrollment = enrollmentService.enrollSubject(student.getId(), testTimetable.getId());
                if (testEnrollment != null) {
                    result.put("test_enrollment", "SUCCESS - ID: " + testEnrollment.getId());
                    
                    // 등록 후 다시 조회해보기
                    List<Enrollment> afterEnrollments = enrollmentService.getEnrollmentsByStudentId(student.getId());
                    result.put("after_enrollment_count", afterEnrollments.size());
                } else {
                    result.put("test_enrollment", "FAILED");
                }
            }
            
        } catch (Exception e) {
            result.put("error", e.getMessage());
            e.printStackTrace();
        }
        
        return result;
    }
    
    @GetMapping("/test-simple")
    @ResponseBody
    public String testSimple() {
        return "Debug controller is working!";
    }
}