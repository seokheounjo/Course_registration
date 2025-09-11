package com.example.registrationweb.controller;

import com.example.registrationweb.model.Enrollment;
import com.example.registrationweb.model.Student;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.service.EnrollmentService;
import com.example.registrationweb.service.StudentService;
import com.example.registrationweb.service.TimetableService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Controller
@RequestMapping("/student")
public class StudentController {

    private final StudentService studentService;
    private final EnrollmentService enrollmentService;
    private final TimetableService timetableService;

    public StudentController(StudentService studentService,
                             EnrollmentService enrollmentService,
                             TimetableService timetableService) {
        this.studentService = studentService;
        this.enrollmentService = enrollmentService;
        this.timetableService = timetableService;
    }

    // 학생 메인 페이지
    @GetMapping
    public String studentMainPage(HttpSession session, Model model) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        model.addAttribute("student", student);

        return "student";
    }

    // 수강 조회 페이지
    @GetMapping("/courses")
    public String viewEnrollments(HttpSession session, Model model) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 수강 신청 내역 가져오기
        List<Enrollment> enrollments = enrollmentService.getEnrollmentsByStudentId(student.getId());
        model.addAttribute("enrollments", enrollments);
        model.addAttribute("student", student);

        return "student/courses";
    }

    // 수강 취소
    @GetMapping("/courses/{enrollmentId}/cancel")
    public String cancelEnrollment(@PathVariable Long enrollmentId,
                                   HttpSession session,
                                   RedirectAttributes redirectAttributes) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 수강 취소
        boolean result = enrollmentService.cancelEnrollment(enrollmentId);

        if (result) {
            redirectAttributes.addFlashAttribute("successMessage", "수강 취소가 완료되었습니다.");
        } else {
            redirectAttributes.addFlashAttribute("errorMessage", "수강 취소에 실패했습니다.");
        }

        return "redirect:/student/courses";
    }

    // 수강 신청 페이지
    @GetMapping("/enroll")
    public String showEnrollmentForm(HttpSession session, Model model) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 강의 목록 가져오기
        List<Timetable> timetables = timetableService.getAllTimetables();

        // 각 시간표에 대한 현재 등록 학생 수 계산 및 학점 정보 추가
        for (Timetable timetable : timetables) {
            long enrollmentCount = enrollmentService.getEnrollmentCountByTimetableId(timetable.getId());

            // 현재 수강 인원 수 설정
            timetable.setEnrolled((int)enrollmentCount);

            // 정원 초과 여부 확인
            if (timetable.getCapacity() != null && enrollmentCount >= timetable.getCapacity()) {
                // 정원이 차 있음을 나타내는 속성 추가
                timetable.setIsFull(true);
            } else {
                timetable.setIsFull(false);
                // 남은 자리 계산
                timetable.setRemainingSeats(timetable.getCapacity() - (int)enrollmentCount);
            }

            // 학년 정보 설정 - 과목의 학년 정보가 없는 경우 기본값 설정
            if (timetable.getSubject() != null && timetable.getSubject().getTargetGrade() != null) {
                timetable.setTargetGrade(timetable.getSubject().getTargetGrade());
            } else {
                timetable.setTargetGrade("전체"); // 기본값을 '전체'로 설정
            }
        }

        // 현재 수강 중인 과목 정보도 가져와서 전달
        List<Enrollment> enrollments = enrollmentService.getEnrollmentsByStudentId(student.getId());
        
        // 디버깅 로그 추가
        System.out.println("DEBUG: Student ID = " + student.getId());
        System.out.println("DEBUG: Enrollments count = " + enrollments.size());
        for (Enrollment e : enrollments) {
            System.out.println("DEBUG: Enrollment - Subject: " + 
                (e.getSubject() != null ? e.getSubject().getName() : "NULL") +
                ", Timetable: " + (e.getTimetable() != null ? e.getTimetable().getDay() : "NULL"));
        }

        model.addAttribute("timetables", timetables);
        model.addAttribute("enrollments", enrollments);
        model.addAttribute("student", student);

        return "student/enroll";
    }

    // 수강 신청 처리 (단일 과목)
    @PostMapping("/enroll")
    public String processEnrollment(@RequestParam Long timetableId,
                                    HttpSession session,
                                    RedirectAttributes redirectAttributes) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 시간표 정보 가져오기
        Timetable timetable = timetableService.getTimetableById(timetableId);
        if (timetable == null) {
            redirectAttributes.addFlashAttribute("errorMessage", "존재하지 않는 과목입니다.");
            return "redirect:/student/enroll";
        }

        // 정원 확인
        long enrollmentCount = enrollmentService.getEnrollmentCountByTimetableId(timetableId);
        if (timetable.getCapacity() != null && enrollmentCount >= timetable.getCapacity()) {
            redirectAttributes.addFlashAttribute("errorMessage", "정원이 초과되어 수강 신청할 수 없습니다.");
            return "redirect:/student/enroll";
        }

        // 수강 신청
        Enrollment enrollment = enrollmentService.enrollSubject(student.getId(), timetableId);

        if (enrollment != null) {
            redirectAttributes.addFlashAttribute("successMessage", "수강 신청이 완료되었습니다.");
        } else {
            redirectAttributes.addFlashAttribute("errorMessage", "수강 신청에 실패했습니다. 이미 수강 중이거나 시간이 겹치는 과목입니다.");
        }

        return "redirect:/student/enroll";
    }

    // 일괄 수강 신청 처리
    @PostMapping("/enroll/bulk")
    public String processBulkEnrollment(@RequestParam String timetableIds,
                                        HttpSession session,
                                        RedirectAttributes redirectAttributes) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 시간표 ID 목록 파싱
        String[] idsArray = timetableIds.split(",");
        List<Long> ids = new ArrayList<>();
        for (String id : idsArray) {
            try {
                ids.add(Long.parseLong(id.trim()));
            } catch (NumberFormatException e) {
                // 유효하지 않은 ID 무시
            }
        }

        if (ids.isEmpty()) {
            redirectAttributes.addFlashAttribute("errorMessage", "선택된 과목이 없습니다.");
            return "redirect:/student/enroll";
        }

        // 일괄 수강 신청 처리
        int successCount = 0;
        List<String> failedSubjects = new ArrayList<>();

        // 과목 중복 체크를 위한 Set
        Set<Long> subjectIds = new HashSet<>();

        for (Long timetableId : ids) {
            // 시간표 정보 가져오기
            Timetable timetable = timetableService.getTimetableById(timetableId);
            if (timetable == null) {
                failedSubjects.add("존재하지 않는 과목");
                continue;
            }

            // 과목 ID 가져오기
            Long subjectId = timetable.getSubject().getId();

            // 이미 처리한 과목인지 확인 (클라이언트 측 중복 선택 방지)
            if (subjectIds.contains(subjectId)) {
                failedSubjects.add(timetable.getSubjectName() + " (중복 선택)");
                continue;
            }

            // 과목 ID 추가
            subjectIds.add(subjectId);

            // 정원 확인
            long enrollmentCount = enrollmentService.getEnrollmentCountByTimetableId(timetableId);
            if (timetable.getCapacity() != null && enrollmentCount >= timetable.getCapacity()) {
                failedSubjects.add(timetable.getSubjectName() + " (정원 초과)");
                continue;
            }

            // 이미 같은 과목을 수강 중인지 확인
            boolean alreadyEnrolled = enrollmentService.isAlreadyEnrolledSubject(student.getId(), subjectId);
            if (alreadyEnrolled) {
                failedSubjects.add(timetable.getSubjectName() + " (이미 수강 중)");
                continue;
            }

            // 학년 제한 확인
            String targetGrade = timetable.getSubject().getTargetGrade();
            if (targetGrade != null && !targetGrade.equals("전체") && !targetGrade.equals(student.getGrade())) {
                failedSubjects.add(timetable.getSubjectName() + " (학년 제한)");
                continue;
            }

            // 수강 신청
            Enrollment enrollment = enrollmentService.enrollSubject(student.getId(), timetableId);
            if (enrollment != null) {
                successCount++;
            } else {
                failedSubjects.add(timetable.getSubjectName() + " (시간 충돌 또는 기타 오류)");
            }
        }

        if (successCount > 0) {
            redirectAttributes.addFlashAttribute("successMessage", successCount + "개 과목의 수강 신청이 완료되었습니다.");
        }

        if (!failedSubjects.isEmpty()) {
            StringBuilder errorMsg = new StringBuilder("다음 과목들의 수강 신청에 실패했습니다: ");
            for (int i = 0; i < failedSubjects.size(); i++) {
                if (i > 0) {
                    errorMsg.append(", ");
                }
                errorMsg.append(failedSubjects.get(i));
            }
            redirectAttributes.addFlashAttribute("errorMessage", errorMsg.toString());
        }

        return "redirect:/student/enroll";
    }

    // 시간표 조회 페이지
    @GetMapping("/timetable")
    public String viewTimetable(HttpSession session, Model model) {
        // 로그인 확인 (학생만 접근 가능)
        if (!"student".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 학생 정보 가져오기
        Student student = studentService.getStudentByStudentId((String) session.getAttribute("username"));
        if (student == null) {
            return "redirect:/login";
        }

        // 수강 신청 내역 가져오기
        List<Enrollment> enrollments = enrollmentService.getEnrollmentsByStudentId(student.getId());
        
        // 디버깅 로그 추가
        System.out.println("DEBUG TIMETABLE: Student ID = " + student.getId());
        System.out.println("DEBUG TIMETABLE: Enrollments count = " + enrollments.size());
        for (Enrollment e : enrollments) {
            System.out.println("DEBUG TIMETABLE: Enrollment - Subject: " + 
                (e.getSubject() != null ? e.getSubject().getName() : "NULL") +
                ", Timetable: " + (e.getTimetable() != null ? e.getTimetable().getDay() : "NULL"));
        }
        
        model.addAttribute("enrollments", enrollments);
        model.addAttribute("student", student);

        return "student/timetable";
    }
}