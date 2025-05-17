package com.example.Course_registration.dto;

import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import com.example.Course_registration.entity.Subject;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class SubjectForm {

    private Long id;           // 수정 시 식별자
    private String name;
    private Integer credits;
    private Integer capacity;
    private String semester;

    private Long professorId;   // 선택된 교수 id (nullable)
    private Long departmentId;  // 선택된 학과 id

    public SubjectForm() {}

    /* Entity → Form */
    public SubjectForm(Subject subject) {
        this.id           = subject.getId();
        this.name         = subject.getName();
        this.credits      = subject.getCredits();
        this.capacity     = subject.getCapacity();
        this.semester     = subject.getSemester();
        this.professorId  = (subject.getProfessor()  != null) ? subject.getProfessor().getId()  : null;
        this.departmentId = (subject.getDepartment() != null) ? subject.getDepartment().getId() : null;
    }

    /* Form → Entity */
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
