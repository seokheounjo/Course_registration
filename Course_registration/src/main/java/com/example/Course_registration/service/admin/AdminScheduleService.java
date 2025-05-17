package com.example.Course_registration.service.admin;

import com.example.Course_registration.entity.SubjectSchedule;
import com.example.Course_registration.repository.SubjectScheduleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminScheduleService {

    private final SubjectScheduleRepository scheduleRepository;

    public List<SubjectSchedule> findAll() {
        return scheduleRepository.findAll();
    }

    public SubjectSchedule findById(Long id) {
        return scheduleRepository.findById(id).orElse(null);
    }

    public void save(SubjectSchedule schedule) {
        scheduleRepository.save(schedule);
    }

    public void delete(Long id) {
        scheduleRepository.deleteById(id);
    }
}
