package com.example.Course_registration.service.admin;

import com.example.Course_registration.dto.AdminSubjectDto;
import com.example.Course_registration.entity.Subject;
import com.example.Course_registration.repository.DepartmentRepository;
import com.example.Course_registration.repository.ProfessorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class SubjectConverter {

    private final DepartmentRepository deptRepo;
    private final ProfessorRepository  profRepo;

    public Subject toEntity(AdminSubjectDto d) {
        Subject s = new Subject();
        s.setId(d.id());
        s.setName(d.name());
        s.setCredits(d.credits());
        s.setCapacity(d.capacity());
        s.setSemester(d.semester());
        s.setDepartment(deptRepo.getReferenceById(d.departmentId()));
        if (d.professorId() != null) {
            s.setProfessor(profRepo.getReferenceById(d.professorId()));
        } else {
            s.setProfessor(null);
        }
        return s;
    }
}
