package com.example.Course_registration.dto;

import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class SubjectForm {

    /* 화면﻿ 입력 필드 */
    private Long id;           // 수정 시 식별자
    private String name;
    private Integer credits;
    private Integer capacity;
    private String semester;

    /* 셀렉트박스에서 넘어오는 PK */
    private Long professorId;   // nullable
    private Long departmentId;

    /* 기본 생성자 */
    public SubjectForm() {}

    /* Entity → Form 변환 */
    public SubjectForm(Subject subject) {
        this.id          = subject.getId();
        this.name        = subject.getName();
        this.credits     = subject.getCredits();
        this.capacity    = subject.getCapacity();
        this.semester    = subject.getSemester();
        this.professorId = (subject.getProfessor()  != null) ? subject.getProfessor().getId()  : null;
        this.departmentId= (subject.getDepartment() != null) ? subject.getDepartment().getId() : null;
    }

    /* Form → Entity 변환 */
    public Subject toEntity(Professor prof, Department dept) {
        Subject s = new Subject();
        s.setId(id);
        s.setName(name);
        s.setCredits(credits);
        s.setCapacity(capacity);
        s.setSemester(semester);
        s.setProfessor(prof);
        s.setDepartment(dept);
        return s;
    }
}
