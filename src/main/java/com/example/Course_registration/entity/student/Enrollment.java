package com.example.Course_registration.entity.student;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "enrollment", uniqueConstraints = {
        @UniqueConstraint(columnNames = {"student_id", "subject_id"})
})
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "student_id", nullable = false)
    private Long studentId;

    @Column(name = "subject_id", nullable = false)
    private Long subjectId;

    @Column(name = "enrolled_at")
    private LocalDateTime enrolledAt = LocalDateTime.now();

    // --- 생성자 ---
    public Enrollment() {}

    public Enrollment(Long studentId, Long subjectId) {
        this.studentId = studentId;
        this.subjectId = subjectId;
    }

    // --- Getter / Setter ---
    public Long getId() { return id; }
    public Long getStudentId() { return studentId; }
    public void setStudentId(Long studentId) { this.studentId = studentId; }

    public Long getSubjectId() { return subjectId; }
    public void setSubjectId(Long subjectId) { this.subjectId = subjectId; }

    public LocalDateTime getEnrolledAt() { return enrolledAt; }
    public void setEnrolledAt(LocalDateTime enrolledAt) { this.enrolledAt = enrolledAt; }
}
