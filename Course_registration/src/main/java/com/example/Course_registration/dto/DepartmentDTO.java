package com.example.Course_registration.dto;

import com.example.Course_registration.entity.Department;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class DepartmentDTO {
    private Long id;
    private String name;
    private boolean selected;

    public DepartmentDTO(Department d, boolean selected) {
        this(d.getId(), d.getName(), selected);
    }
}
