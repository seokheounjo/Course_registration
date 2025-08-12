package com.example.registrationweb.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

@Entity
@Table(name = "timetables")
public class Timetable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "subject_id")
    private Subject subject;

    @Transient // DB에 저장하지 않는 필드
    private String subjectName;

    @NotBlank(message = "요일은 필수 입력 항목입니다")
    @Column(name = "class_day") // day -> class_day로 변경
    private String day;

    @NotBlank(message = "시작 시간은 필수 입력 항목입니다")
    private String startTime;

    @NotBlank(message = "종료 시간은 필수 입력 항목입니다")
    private String endTime;

    @NotBlank(message = "강의실은 필수 입력 항목입니다")
    private String room;

    @ManyToOne
    @JoinColumn(name = "professor_id")
    private Professor professor;

    @Transient // DB에 저장하지 않는 필드
    private String professorName;

    @NotNull(message = "정원은 필수 입력 항목입니다")
    @Min(value = 1, message = "정원은 최소 1명 이상이어야 합니다")
    private Integer capacity;

    // 강의계획서 파일명
    private String syllabusFileName;

    // 강의계획서 파일 경로
    private String syllabusFilePath;

    @Transient // DB에 저장하지 않는 필드
    private Boolean isFull;

    @Transient // DB에 저장하지 않는 필드
    private Integer remainingSeats;

    @Transient // DB에 저장하지 않는 필드 - 현재 수강 인원 수를 저장하는 필드 추가
    private Integer enrolled;

    @Transient // DB에 저장하지 않는 필드 - 수강 대상 학년
    private String targetGrade;

    public Timetable() {
    }

    public Timetable(Long id, Subject subject, String day, String startTime, String endTime, String room, Professor professor, Integer capacity) {
        this.id = id;
        this.subject = subject;
        this.day = day;
        this.startTime = startTime;
        this.endTime = endTime;
        this.room = room;
        this.professor = professor;
        this.capacity = capacity;
    }

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Subject getSubject() {
        return subject;
    }

    public void setSubject(Subject subject) {
        this.subject = subject;
    }

    public Long getSubjectId() {
        return subject != null ? subject.getId() : null;
    }

    public String getSubjectName() {
        return subject != null ? subject.getName() : subjectName;
    }

    public void setSubjectName(String subjectName) {
        this.subjectName = subjectName;
    }

    public String getDay() {
        return day;
    }

    public void setDay(String day) {
        this.day = day;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getEndTime() {
        return endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public String getRoom() {
        return room;
    }

    public void setRoom(String room) {
        this.room = room;
    }

    public Professor getProfessor() {
        return professor;
    }

    public void setProfessor(Professor professor) {
        this.professor = professor;
    }

    public Long getProfessorId() {
        return professor != null ? professor.getId() : null;
    }

    public String getProfessorName() {
        return professor != null ? professor.getName() : professorName;
    }

    public void setProfessorName(String professorName) {
        this.professorName = professorName;
    }

    public Integer getCapacity() {
        return capacity;
    }

    public void setCapacity(Integer capacity) {
        this.capacity = capacity;
    }

    public String getSyllabusFileName() {
        return syllabusFileName;
    }

    public void setSyllabusFileName(String syllabusFileName) {
        this.syllabusFileName = syllabusFileName;
    }

    public String getSyllabusFilePath() {
        return syllabusFilePath;
    }

    public void setSyllabusFilePath(String syllabusFilePath) {
        this.syllabusFilePath = syllabusFilePath;
    }

    public Boolean getIsFull() {
        return isFull;
    }

    public void setIsFull(Boolean isFull) {
        this.isFull = isFull;
    }

    public Integer getRemainingSeats() {
        return remainingSeats;
    }

    public void setRemainingSeats(Integer remainingSeats) {
        this.remainingSeats = remainingSeats;
    }

    public Integer getEnrolled() {
        return enrolled;
    }

    public void setEnrolled(Integer enrolled) {
        this.enrolled = enrolled;
    }

    public String getTargetGrade() {
        return targetGrade;
    }

    public void setTargetGrade(String targetGrade) {
        this.targetGrade = targetGrade;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Timetable timetable = (Timetable) o;
        return Objects.equals(id, timetable.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}