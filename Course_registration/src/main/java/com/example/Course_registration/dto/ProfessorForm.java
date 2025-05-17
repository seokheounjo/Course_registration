package com.example.Course_registration.dto;

import com.example.Course_registration.entity.Department;
import com.example.Course_registration.entity.Professor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ProfessorForm {
    private Long id;
    private String name;
    private String email;
    private String password;
    private Long departmentId;

    public ProfessorForm() {}

    public ProfessorForm(Professor professor) {
        this.id = professor.getId();
        this.name = professor.getName();
        this.email = professor.getEmail();
        this.password = professor.getPassword();
        this.departmentId = professor.getDepartment() != null ? professor.getDepartment().getId() : null;
    }

    public Professor toEntity(Department department) {
        Professor professor = new Professor();
        professor.setId(this.id);
        professor.setName(this.name);
        professor.setEmail(this.email);
        professor.setPassword(this.password);
        professor.setDepartment(department);
        return professor;
    }
}
