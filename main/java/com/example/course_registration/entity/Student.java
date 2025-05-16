package com.example.course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    private String studentNumber; // 아이디

    private String password;
    private String name;
    private String email;
    private String phone;
    private String grade;

    @ManyToOne
    @JoinColumn(name = "department_id")
    private Department department;
}



