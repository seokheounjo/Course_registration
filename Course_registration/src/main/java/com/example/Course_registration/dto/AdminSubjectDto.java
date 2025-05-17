package com.example.Course_registration.dto;

import jakarta.validation.constraints.*;

public record AdminSubjectDto(
        Long   id,
        @NotBlank String name,
        @Min(1)   int    credits,
        @Min(1)   int    capacity,
        @NotBlank String semester,
        Long   professorId,   // nullable: 미배정
        @NotNull Long departmentId
) {}
