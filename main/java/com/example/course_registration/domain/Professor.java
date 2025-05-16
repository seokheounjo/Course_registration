package com.example.course_registration.domain;
import com.example.course_registration.entity.Subject;
import jakarta.persistence.*;

import java.util.List;

@Entity
@Table(name = "professor")
public class Professor {

    @Id
    private Long id;

    private String name;

    @Column(unique = true)
    private String email;

    private String password;

    @Column(name = "department_id")
    private Long departmentId;

//    @OneToMany(mappedBy = "professor", cascade = CascadeType.REMOVE, orphanRemoval = true)
//    private List<Subject> subjects;

    // --- getters & setters ---
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public Long getDepartmentId() { return departmentId; }
    public void setDepartmentId(Long departmentId) { this.departmentId = departmentId; }
}
