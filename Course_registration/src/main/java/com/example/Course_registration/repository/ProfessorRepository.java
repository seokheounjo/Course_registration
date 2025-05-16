package com.example.Course_registration.repository;

import com.example.Course_registration.domain.Professor;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfessorRepository extends JpaRepository<Professor, Long> { }
