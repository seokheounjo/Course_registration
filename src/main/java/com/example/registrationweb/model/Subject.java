package com.example.registrationweb.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

@Entity
@Table(name = "subjects")
public class Subject {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    @NotBlank(message = "과목 코드는 필수 입력 항목입니다")
    private String code;

    @NotBlank(message = "과목명은 필수 입력 항목입니다")
    private String name;

    @NotNull(message = "학점 수는 필수 입력 항목입니다")
    @Min(value = 1, message = "학점은 최소 1점 이상이어야 합니다")
    private Integer credits;

    private String department;

    @ManyToOne
    @JoinColumn(name = "professor_id")
    private Professor professor;

    @Transient // DB에 저장하지 않는 필드
    private String professorName;

    public Subject() {
    }

    public Subject(Long id, String code, String name, Integer credits, String department, Professor professor) {
        this.id = id;
        this.code = code;
        this.name = name;
        this.credits = credits;
        this.department = department;
        this.professor = professor;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getCredits() {
        return credits;
    }

    public void setCredits(Integer credits) {
        this.credits = credits;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
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

    public void setProfessorId(Long professorId) {
        if (professorId != null) {
            this.professor = new Professor();
            this.professor.setId(professorId);
        } else {
            this.professor = null;
        }
    }

    public String getProfessorName() {
        return professor != null ? professor.getName() : professorName;
    }

    public void setProfessorName(String professorName) {
        this.professorName = professorName;
    }

    // 대상 학년 필드 추가
    @Column(name = "target_grade")
    private String targetGrade = "전체"; // 기본값 설정

    // targetGrade 필드의 getter와 setter
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
        Subject subject = (Subject) o;
        return Objects.equals(id, subject.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}