package com.example.registrationweb.controller;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.service.EnrollmentService;
import com.example.registrationweb.service.ProfessorService;
import com.example.registrationweb.service.SubjectService;
import com.example.registrationweb.service.TimetableService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.annotation.PostConstruct;

@Controller
@RequestMapping("/integrated")
public class IntegratedController {

    private final SubjectService subjectService;
    private final TimetableService timetableService;
    private final ProfessorService professorService;
    private final EnrollmentService enrollmentService;

    @Value("${file.upload.directory:uploads/syllabus}")
    private String uploadDirectory;

    public IntegratedController(SubjectService subjectService,
                                TimetableService timetableService,
                                ProfessorService professorService,
                                EnrollmentService enrollmentService) {
        this.subjectService = subjectService;
        this.timetableService = timetableService;
        this.professorService = professorService;
        this.enrollmentService = enrollmentService;
    }

    @PostConstruct
    public void init() {
        createUploadDirectoryIfNotExists();
    }

    private void createUploadDirectoryIfNotExists() {
        try {
            File directory = new File(uploadDirectory);
            if (!directory.exists()) {
                directory.mkdirs();
            }
        } catch (Exception e) {
            System.err.println("Failed to create upload directory: " + e.getMessage());
            // 에러를 기록하지만 애플리케이션은 계속 실행되도록 허용
        }
    }

    @GetMapping("/subject-info")
    @ResponseBody
    public Map<String, Object> getSubjectInfo(@RequestParam String code) {
        Map<String, Object> result = new HashMap<>();

        Subject subject = subjectService.getSubjectByCode(code);
        if (subject != null) {
            result.put("found", true);
            result.put("name", subject.getName());
            result.put("credits", subject.getCredits());
            result.put("department", subject.getDepartment());
        } else {
            result.put("found", false);
        }

        return result;
    }

    @GetMapping
    public String listIntegrated(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 통합된 과목 및 시간표 정보 가져오기
        List<Timetable> timetables = timetableService.getAllTimetables();
        List<Map<String, Object>> integratedList = new ArrayList<>();

        for (Timetable timetable : timetables) {
            Map<String, Object> item = new HashMap<>();

            // 기본 시간표 정보 추가
            item.put("id", timetable.getId());
            item.put("day", timetable.getDay());
            item.put("startTime", timetable.getStartTime());
            item.put("endTime", timetable.getEndTime());
            item.put("room", timetable.getRoom());
            item.put("professorName", timetable.getProfessorName());
            item.put("capacity", timetable.getCapacity());
            item.put("syllabusFileName", timetable.getSyllabusFileName());

            // 과목 정보 가져오기
            Subject subject = timetable.getSubject();
            if (subject != null) {
                item.put("subjectId", subject.getId());
                item.put("subjectCode", subject.getCode());
                item.put("subjectName", subject.getName());
                item.put("credits", subject.getCredits());
                item.put("department", subject.getDepartment());
                item.put("professorId", subject.getProfessor().getId());
            } else {
                item.put("subjectId", null);
                item.put("subjectCode", "");
                item.put("subjectName", timetable.getSubjectName());
                item.put("credits", 0);
                item.put("department", "");
                item.put("professorId", timetable.getProfessorId());
            }

            integratedList.add(item);
        }

        model.addAttribute("timetables", integratedList);
        return "integrated/list";
    }

    @GetMapping("/new")
    public String showNewForm(Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 빈 Timetable 객체의 개별 필드를 모델에 추가
        model.addAttribute("id", "");
        model.addAttribute("subjectId", "");
        model.addAttribute("subjectCode", "");
        model.addAttribute("subjectName", "");
        model.addAttribute("credits", "");
        model.addAttribute("department", "");
        model.addAttribute("day", "");
        model.addAttribute("startTime", "");
        model.addAttribute("endTime", "");
        model.addAttribute("room", "");
        model.addAttribute("professorId", "");
        model.addAttribute("capacity", "30"); // 기본값 30으로 설정
        model.addAttribute("isNew", true);

        // 교수 목록 추가
        model.addAttribute("professors", professorService.getAllProfessors());

        return "integrated/form";
    }

    @PostMapping
    public String saveIntegrated(@RequestParam String subjectCode,
                                 @RequestParam String subjectName,
                                 @RequestParam Integer credits,
                                 @RequestParam String department,
                                 @RequestParam Long professorId,
                                 @RequestParam String day,
                                 @RequestParam String startTime,
                                 @RequestParam String endTime,
                                 @RequestParam String room,
                                 @RequestParam Integer capacity,
                                 @RequestParam(value = "syllabusFile", required = false) MultipartFile syllabusFile,
                                 HttpSession session,
                                 RedirectAttributes redirectAttributes) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 수업 시간 확인 (최소 1시간 이상)
        LocalTime start = LocalTime.parse(startTime);
        LocalTime end = LocalTime.parse(endTime);
        long minutesDiff = ChronoUnit.MINUTES.between(start, end);

        if (minutesDiff < 60) {
            redirectAttributes.addFlashAttribute("error", "수업 시간은 최소 1시간 이상이어야 합니다.");

            // 입력값 유지를 위해 기존 입력 데이터를 flash attribute로 저장
            redirectAttributes.addFlashAttribute("subjectCode", subjectCode);
            redirectAttributes.addFlashAttribute("subjectName", subjectName);
            redirectAttributes.addFlashAttribute("credits", credits);
            redirectAttributes.addFlashAttribute("department", department);
            redirectAttributes.addFlashAttribute("professorId", professorId);
            redirectAttributes.addFlashAttribute("day", day);
            redirectAttributes.addFlashAttribute("startTime", startTime);
            redirectAttributes.addFlashAttribute("endTime", endTime);
            redirectAttributes.addFlashAttribute("room", room);
            redirectAttributes.addFlashAttribute("capacity", capacity);

            return "redirect:/integrated/new";
        }

        // 시간대와 강의실 중복 체크
        boolean roomTimeConflict = timetableService.checkRoomTimeConflict(day, startTime, endTime, room, null);
        if (roomTimeConflict) {
            redirectAttributes.addFlashAttribute("error", "해당 시간대에 같은 강의실에서 이미 수업이 진행 중입니다.");

            // 입력값 유지
            redirectAttributes.addFlashAttribute("subjectCode", subjectCode);
            redirectAttributes.addFlashAttribute("subjectName", subjectName);
            redirectAttributes.addFlashAttribute("credits", credits);
            redirectAttributes.addFlashAttribute("department", department);
            redirectAttributes.addFlashAttribute("professorId", professorId);
            redirectAttributes.addFlashAttribute("day", day);
            redirectAttributes.addFlashAttribute("startTime", startTime);
            redirectAttributes.addFlashAttribute("endTime", endTime);
            redirectAttributes.addFlashAttribute("room", room);
            redirectAttributes.addFlashAttribute("capacity", capacity);

            return "redirect:/integrated/new";
        }

        // 교수 정보 가져오기
        Professor professor = professorService.getProfessorById(professorId);
        if (professor == null) {
            return "redirect:/integrated";
        }

        // 1. 과목 저장 (기존 과목 코드가 있으면 그 과목을 재사용)
        Subject subject;
        Subject existingSubject = subjectService.getSubjectByCode(subjectCode);

        if (existingSubject != null) {
            // 기존 과목 활용 (단, 정보는 입력한 값으로 업데이트하지 않음)
            subject = existingSubject;
        } else {
            // 새 과목 생성
            subject = new Subject();
            subject.setCode(subjectCode);
            subject.setName(subjectName);
            subject.setCredits(credits);
            subject.setDepartment(department);
            subject.setProfessor(professor);
            subject = subjectService.saveSubject(subject);
        }

        // 2. 시간표 저장
        Timetable timetable = new Timetable();
        timetable.setSubject(subject);
        timetable.setDay(day);
        timetable.setStartTime(startTime);
        timetable.setEndTime(endTime);
        timetable.setRoom(room);
        timetable.setProfessor(professor);
        timetable.setCapacity(capacity);

        // 3. 강의계획서 파일 저장
        if (syllabusFile != null && !syllabusFile.isEmpty()) {
            try {
                // 고유한 파일명 생성
                String originalFilename = syllabusFile.getOriginalFilename();
                String extension = "";
                if (originalFilename != null && originalFilename.contains(".")) {
                    extension = originalFilename.substring(originalFilename.lastIndexOf("."));
                }
                String newFilename = UUID.randomUUID().toString() + extension;

                // 파일 저장 경로 설정
                Path filePath = Paths.get(uploadDirectory, newFilename);

                // 파일 저장
                Files.copy(syllabusFile.getInputStream(), filePath);

                // 시간표에 파일 정보 설정
                timetable.setSyllabusFileName(originalFilename);
                timetable.setSyllabusFilePath(filePath.toString().replace('\\', '/'));

            } catch (IOException e) {
                redirectAttributes.addFlashAttribute("error", "강의계획서 파일 업로드에 실패했습니다: " + e.getMessage());
                return "redirect:/integrated/new";
            }
        }

        timetableService.saveTimetable(timetable);

        redirectAttributes.addFlashAttribute("success", "새 과목 및 시간표가 성공적으로 추가되었습니다.");
        return "redirect:/integrated";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        Timetable timetable = timetableService.getTimetableById(id);
        if (timetable == null) {
            return "redirect:/integrated";
        }

        Subject subject = timetable.getSubject();
        if (subject == null) {
            return "redirect:/integrated";
        }

        // 통합된 필드 설정
        model.addAttribute("id", timetable.getId());
        model.addAttribute("subjectId", subject.getId());
        model.addAttribute("subjectCode", subject.getCode());
        model.addAttribute("subjectName", subject.getName());
        model.addAttribute("credits", subject.getCredits());
        model.addAttribute("department", subject.getDepartment());
        model.addAttribute("day", timetable.getDay());
        model.addAttribute("startTime", timetable.getStartTime());
        model.addAttribute("endTime", timetable.getEndTime());
        model.addAttribute("room", timetable.getRoom());
        model.addAttribute("professorId", timetable.getProfessor().getId());
        model.addAttribute("capacity", timetable.getCapacity());
        model.addAttribute("syllabusFileName", timetable.getSyllabusFileName());
        model.addAttribute("isNew", false);

        // 교수 목록 추가
        model.addAttribute("professors", professorService.getAllProfessors());

        // 현재 등록된 학생 수 추가
        model.addAttribute("enrollmentCount", enrollmentService.getEnrollmentCountByTimetableId(id));

        return "integrated/form";
    }

    @PostMapping("/{id}")
    public String updateIntegrated(@PathVariable Long id,
                                   @RequestParam String subjectCode,
                                   @RequestParam String subjectName,
                                   @RequestParam Integer credits,
                                   @RequestParam String department,
                                   @RequestParam Long professorId,
                                   @RequestParam String day,
                                   @RequestParam String startTime,
                                   @RequestParam String endTime,
                                   @RequestParam String room,
                                   @RequestParam Integer capacity,
                                   @RequestParam Long subjectId,
                                   @RequestParam(value = "syllabusFile", required = false) MultipartFile syllabusFile,
                                   HttpSession session,
                                   RedirectAttributes redirectAttributes) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 과목 정보 가져오기
        Subject existingSubject = subjectService.getSubjectById(subjectId);
        if (existingSubject == null) {
            return "redirect:/integrated";
        }

        // 수업 시간 확인 (최소 1시간 이상)
        LocalTime start = LocalTime.parse(startTime);
        LocalTime end = LocalTime.parse(endTime);
        long minutesDiff = ChronoUnit.MINUTES.between(start, end);

        if (minutesDiff < 60) {
            redirectAttributes.addFlashAttribute("error", "수업 시간은 최소 1시간 이상이어야 합니다.");
            return "redirect:/integrated/" + id + "/edit";
        }

        // 시간대와 강의실 중복 체크 (자기 자신은 제외)
        boolean roomTimeConflict = timetableService.checkRoomTimeConflict(day, startTime, endTime, room, id);
        if (roomTimeConflict) {
            redirectAttributes.addFlashAttribute("error", "해당 시간대에 같은 강의실에서 이미 수업이 진행 중입니다.");
            return "redirect:/integrated/" + id + "/edit";
        }

        // 교수 정보 가져오기
        Professor professor = professorService.getProfessorById(professorId);
        if (professor == null) {
            return "redirect:/integrated";
        }

        // 과목 코드 변경 여부 확인
        boolean codeChanged = !existingSubject.getCode().equals(subjectCode);
        Subject targetSubject;

        if (codeChanged) {
            // 과목 코드가 변경됨 - 기존 과목 코드인지 확인
            Subject codeExistingSubject = subjectService.getSubjectByCode(subjectCode);
            if (codeExistingSubject != null) {
                // 기존 과목 코드로 변경 - 해당 과목 사용
                targetSubject = codeExistingSubject;
            } else {
                // 새로운 과목 코드로 변경 - 기존 과목 정보 업데이트
                existingSubject.setCode(subjectCode);
                existingSubject.setName(subjectName);
                existingSubject.setCredits(credits);
                existingSubject.setDepartment(department);
                existingSubject.setProfessor(professor);
                targetSubject = subjectService.updateSubject(subjectId, existingSubject);
            }
        } else {
            // 기존 과목 코드 유지 - 기존 과목 정보 업데이트
            existingSubject.setName(subjectName);
            existingSubject.setCredits(credits);
            existingSubject.setDepartment(department);
            existingSubject.setProfessor(professor);
            targetSubject = subjectService.updateSubject(subjectId, existingSubject);
        }

        // 시간표 업데이트
        Timetable timetable = timetableService.getTimetableById(id);
        if (timetable != null) {
            timetable.setSubject(targetSubject);
            timetable.setDay(day);
            timetable.setStartTime(startTime);
            timetable.setEndTime(endTime);
            timetable.setRoom(room);
            timetable.setProfessor(professor);
            timetable.setCapacity(capacity);

            // 강의계획서 파일 업데이트
            if (syllabusFile != null && !syllabusFile.isEmpty()) {
                try {
                    // 기존 파일이 있다면 삭제
                    if (timetable.getSyllabusFilePath() != null) {
                        Path existingFile = Paths.get(timetable.getSyllabusFilePath());
                        Files.deleteIfExists(existingFile);
                    }

                    // 고유한 파일명 생성
                    String originalFilename = syllabusFile.getOriginalFilename();
                    String extension = "";
                    if (originalFilename != null && originalFilename.contains(".")) {
                        extension = originalFilename.substring(originalFilename.lastIndexOf("."));
                    }
                    String newFilename = UUID.randomUUID().toString() + extension;

                    // 파일 저장 경로 설정
                    Path filePath = Paths.get(uploadDirectory, newFilename);

                    // 파일 저장
                    Files.copy(syllabusFile.getInputStream(), filePath);

                    // 시간표에 파일 정보 설정
                    timetable.setSyllabusFileName(originalFilename);
                    timetable.setSyllabusFilePath(filePath.toString().replace('\\', '/'));

                } catch (IOException e) {
                    redirectAttributes.addFlashAttribute("error", "강의계획서 파일 업로드에 실패했습니다: " + e.getMessage());
                    return "redirect:/integrated/" + id + "/edit";
                }
            }

            timetableService.updateTimetable(id, timetable);
        }

        redirectAttributes.addFlashAttribute("success", "과목 및 시간표가 성공적으로 수정되었습니다.");
        return "redirect:/integrated";
    }

    @GetMapping("/{id}/delete")
    public String deleteIntegrated(@PathVariable Long id, HttpSession session) {
        // 로그인 확인 (관리자만 접근 가능)
        if (!"admin".equals(session.getAttribute("user"))) {
            return "redirect:/login";
        }

        // 시간표 정보 가져오기
        Timetable timetable = timetableService.getTimetableById(id);
        if (timetable != null) {
            // 연결된 강의계획서 파일 삭제
            if (timetable.getSyllabusFilePath() != null) {
                try {
                    Path filePath = Paths.get(timetable.getSyllabusFilePath());
                    Files.deleteIfExists(filePath);
                } catch (IOException e) {
                    // 파일 삭제 실패 로그 출력
                    System.err.println("Failed to delete syllabus file: " + e.getMessage());
                }
            }

            // 1. 시간표 삭제
            timetableService.deleteTimetable(id);

            // 2. 연결된 과목도 삭제
            if (timetable.getSubject() != null) {
                subjectService.deleteSubject(timetable.getSubject().getId());
            }
        }

        return "redirect:/integrated";
    }

    @GetMapping("/syllabus/{id}")
    public String downloadSyllabus(@PathVariable Long id, HttpSession session, RedirectAttributes redirectAttributes) {
        // 로그인 확인
        if (session.getAttribute("user") == null) {
            return "redirect:/login";
        }

        Timetable timetable = timetableService.getTimetableById(id);
        if (timetable == null || timetable.getSyllabusFilePath() == null) {
            redirectAttributes.addFlashAttribute("error", "강의계획서를 찾을 수 없습니다.");
            return "redirect:/integrated";
        }

        // 파일 경로의 백슬래시를 포워드 슬래시로 변환
        String filePath = timetable.getSyllabusFilePath().replace('\\', '/');

        // 파일 다운로드 처리를 위해 파일 경로 반환
        return "redirect:/download?file=" + filePath;
    }
}