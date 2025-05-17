package com.example.Course_registration.entity;

import com.example.Course_registration.entity.Professor;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.util.ArrayList;
import java.util.List;

@Entity
@Getter @Setter
public class Subject {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private Integer credits;
    private Integer capacity;
    private String semester;

    @ManyToOne(optional = true)
    @JoinColumn(
            name = "professor_id",
            nullable = true,  // ← null 허용 (DB 제약조건)
            foreignKey = @ForeignKey(name = "fk_subject_professor")
    )
    private Professor professor;


    @ManyToOne
    @JoinColumn(name = "department_id", foreignKey = @ForeignKey(name = "fk_subject_department"))
    private Department department;



    @OneToMany(mappedBy = "subject", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SubjectSchedule> schedules = new ArrayList<>();

    @OneToMany(mappedBy = "subject", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Enrollment> enrollments = new ArrayList<>();
}
