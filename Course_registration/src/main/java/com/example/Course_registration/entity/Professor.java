package com.example.Course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter @Setter
public class Professor {

    /** ➊ 템플릿 {{#selected}}…{{/selected}} 용 */
    @Transient
    private boolean selected;

    public boolean isSelected() { return selected; }
    public void setSelected(boolean selected) { this.selected = selected; }

    /*------------------------ 기존 필드 ------------------------*/
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
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

    /* ➋ Mustache 의 {{name}} 등 바인딩 오류 방지 – 명시적 getter */
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Department getDepartment() { return department; }
}
