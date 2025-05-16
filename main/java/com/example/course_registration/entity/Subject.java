package com.example.course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "subject")
public class Subject {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private Integer credits;

    @Column(nullable = false)
    private Integer capacity;

    @Column(nullable = false)
    private String semester;

    @Column(name = "professor_id", nullable = false)
    private Long professorId;

    @Column(name = "department_id", nullable = false)
    private Long departmentId;

}
