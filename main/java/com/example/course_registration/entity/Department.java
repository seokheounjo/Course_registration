package com.example.course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class Department {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String office;

    // Mustache 템플릿에서 사용할 선택 여부
    @Transient
    private boolean selected;
}
