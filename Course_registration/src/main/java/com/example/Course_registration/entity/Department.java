package com.example.Course_registration.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter @Setter
public class Department {

    @Transient                      // ➊ 템플릿에서 체크표시 용
    private boolean selected;

    public boolean isSelected() { return selected; }
    public void setSelected(boolean selected) { this.selected = selected; }

    /*------------------------ 기존 필드 ------------------------*/
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String office;

    /* Mustache 안전용 명시적 getter */
    public String getName() { return name; }
    public String getOffice() { return office; }
}
