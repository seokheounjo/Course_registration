package com.example.registrationweb.repository;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface SubjectRepository extends JpaRepository<Subject, Long> {
    Optional<Subject> findByCode(String code);
    boolean existsByCode(String code);
    List<Subject> findByProfessor(Professor professor);

}