package com.example.registrationweb.model;

import jakarta.persistence.*;
import java.util.Objects;

@Entity
@Table(name = "enrollments", uniqueConstraints = {
        @UniqueConstraint(columnNames = {"student_id", "subject_id"})
})
public class Enrollment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @ManyToOne
    @JoinColumn(name = "subject_id", nullable = false)
    private Subject subject;

    @Transient // DB에 저장하지 않는 필드
    private String subjectName;

    @Transient // DB에 저장하지 않는 필드
    private String professorName;

    @ManyToOne
    @JoinColumn(name = "timetable_id", nullable = false)
    private Timetable timetable;

    @Transient // DB에 저장하지 않는 필드
    private String day;

    @Transient // DB에 저장하지 않는 필드
    private String startTime;

    @Transient // DB에 저장하지 않는 필드
    private String endTime;

    @Transient // DB에 저장하지 않는 필드
    private String room;

    public Enrollment() {
    }

    public Enrollment(Long id, Student student, Subject subject, Timetable timetable) {
        this.id = id;
        this.student = student;
        this.subject = subject;
        this.timetable = timetable;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Student getStudent() {
        return student;
    }

    public void setStudent(Student student) {
        this.student = student;
    }

    public Long getStudentId() {
        return student != null ? student.getId() : null;
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

    public String getProfessorName() {
        return subject != null && subject.getProfessor() != null ?
                subject.getProfessor().getName() : professorName;
    }

    public void setProfessorName(String professorName) {
        this.professorName = professorName;
    }

    public Timetable getTimetable() {
        return timetable;
    }

    public void setTimetable(Timetable timetable) {
        this.timetable = timetable;
    }

    public Long getTimetableId() {
        return timetable != null ? timetable.getId() : null;
    }

    public String getDay() {
        return timetable != null ? timetable.getDay() : day;
    }

    public void setDay(String day) {
        this.day = day;
    }

    public String getStartTime() {
        return timetable != null ? timetable.getStartTime() : startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getEndTime() {
        return timetable != null ? timetable.getEndTime() : endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public String getRoom() {
        return timetable != null ? timetable.getRoom() : room;
    }

    public void setRoom(String room) {
        this.room = room;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Enrollment that = (Enrollment) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}