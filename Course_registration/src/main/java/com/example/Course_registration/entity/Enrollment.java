package com.example.Course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "student_id", foreignKey = @ForeignKey(name = "fk_enrollment_student"))
    private Student student;

    @ManyToOne
    @JoinColumn(name = "subject_id", foreignKey = @ForeignKey(name = "fk_enrollment_subject"))
    private Subject subject;

    private String status;

    public Enrollment() {}  // 기본 생성자

    public Enrollment(Long studentId, Long subjectId) {
        this.student = new Student();
        this.student.setId(studentId);

        this.subject = new Subject();
        this.subject.setId(subjectId);
    }
    @Column(name = "enrolled_at")
    private LocalDateTime enrolledAt = LocalDateTime.now();

    @PrePersist
    protected void onCreate() {
        this.enrolledAt = LocalDateTime.now();
    }


}

