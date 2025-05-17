package com.example.Course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class Professor {
    @Transient
    private boolean selected;
    public boolean isSelected() { return selected; }
    public void setSelected(boolean selected) { this.selected = selected; }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 이거 반드시 필요
    private Long id;


    @Column(nullable = false)
    private String name;

    @Column(unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    // 연쇄 삭제 방지 → 단방향 관계 유지 (필요 시 아래 주석 해제)
    // @OneToMany(mappedBy = "professor")
    // private List<Subject> subjects;

    // Mustache의 {{name}} {{email}} 등 필드 바인딩 오류 방지를 위해 명시적으로 Getter 작성 (Lombok 불신 시)
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getPassword() { return password; }
    public Department getDepartment() { return department; }
}
