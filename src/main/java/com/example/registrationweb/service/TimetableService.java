package com.example.registrationweb.service;

import com.example.registrationweb.model.Professor;
import com.example.registrationweb.model.Subject;
import com.example.registrationweb.model.Timetable;
import com.example.registrationweb.repository.ProfessorRepository;
import com.example.registrationweb.repository.SubjectRepository;
import com.example.registrationweb.repository.TimetableRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalTime;
import java.util.List;

@Service
public class TimetableService {
    private final TimetableRepository timetableRepository;
    private final SubjectRepository subjectRepository;
    private final ProfessorRepository professorRepository;

    public TimetableService(TimetableRepository timetableRepository,
                            SubjectRepository subjectRepository,
                            ProfessorRepository professorRepository) {
        this.timetableRepository = timetableRepository;
        this.subjectRepository = subjectRepository;
        this.professorRepository = professorRepository;

        // 초기 데이터는 DB 설정 후 데이터가 로드된 후에 추가합니다
    }

    @Transactional(readOnly = true)
    public List<Timetable> getAllTimetables() {
        return timetableRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Timetable getTimetableById(Long id) {
        return timetableRepository.findById(id).orElse(null);
    }

    @Transactional(readOnly = true)
    public boolean checkRoomTimeConflict(String day, String startTime, String endTime, String room, Long excludeTimetableId) {
        List<Timetable> timetables = timetableRepository.findAll();
        LocalTime newStartTime = LocalTime.parse(startTime);
        LocalTime newEndTime = LocalTime.parse(endTime);

        for (Timetable timetable : timetables) {
            // 자기 자신은 체크하지 않음 (수정 시)
            if (excludeTimetableId != null && timetable.getId().equals(excludeTimetableId)) {
                continue;
            }

            if (timetable.getDay().equals(day) && timetable.getRoom().equals(room)) {
                LocalTime existingStartTime = LocalTime.parse(timetable.getStartTime());
                LocalTime existingEndTime = LocalTime.parse(timetable.getEndTime());

                // 시간 겹침 확인 로직
                if ((newStartTime.isBefore(existingEndTime) && newEndTime.isAfter(existingStartTime))) {
                    return true; // 충돌 발생
                }
            }
        }

        return false; // 충돌 없음
    }

    @Transactional
    public Timetable saveTimetable(Timetable timetable) {
        // Subject 설정
        if (timetable.getSubject() == null && timetable.getSubjectId() != null) {
            subjectRepository.findById(timetable.getSubjectId())
                    .ifPresent(timetable::setSubject);
        }

        // Professor 설정
        if (timetable.getProfessor() == null && timetable.getProfessorId() != null) {
            professorRepository.findById(timetable.getProfessorId())
                    .ifPresent(timetable::setProfessor);
        }

        // 기본 정원 설정 (null인 경우)
        if (timetable.getCapacity() == null) {
            timetable.setCapacity(20); // 기본값 20으로 설정
        }

        return timetableRepository.save(timetable);
    }

    @Transactional
    public boolean deleteTimetable(Long id) {
        if (timetableRepository.existsById(id)) {
            timetableRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional
    public Timetable updateTimetable(Long id, Timetable timetable) {
        if (timetableRepository.existsById(id)) {
            timetable.setId(id);

            // Subject 설정
            if (timetable.getSubject() == null && timetable.getSubjectId() != null) {
                subjectRepository.findById(timetable.getSubjectId())
                        .ifPresent(timetable::setSubject);
            }

            // Professor 설정
            if (timetable.getProfessor() == null && timetable.getProfessorId() != null) {
                professorRepository.findById(timetable.getProfessorId())
                        .ifPresent(timetable::setProfessor);
            }

            return timetableRepository.save(timetable);
        }
        return null;
    }

    // 초기 샘플 데이터 로드
    @Transactional
    public void loadSampleData() {
        if (timetableRepository.count() > 0) {
            return; // 이미 데이터가 있으면 로드하지 않음
        }

        List<Subject> subjects = subjectRepository.findAll();
        List<Professor> professors = professorRepository.findAll();

        if (subjects.size() < 4 || professors.size() < 3) {
            return; // 과목이나 교수 데이터가 부족하면 로드하지 않음
        }

        Subject subject1 = subjects.get(0); // 컴퓨터 개론
        Subject subject2 = subjects.get(1); // 자료구조
        Subject subject3 = subjects.get(2); // 전자공학 개론
        Subject subject4 = subjects.get(3); // 경영학 원론

        Professor professor1 = professors.get(0); // 김교수
        Professor professor2 = professors.get(1); // 이교수
        Professor professor3 = professors.get(2); // 박교수

        Timetable timetable1 = new Timetable(null, subject1, "월요일", "09:00", "10:30", "공학관 101", professor1, 30);
        Timetable timetable2 = new Timetable(null, subject2, "화요일", "11:00", "12:30", "공학관 202", professor1, 25);
        Timetable timetable3 = new Timetable(null, subject3, "수요일", "13:00", "14:30", "공학관 303", professor2, 20);
        Timetable timetable4 = new Timetable(null, subject4, "목요일", "15:00", "16:30", "경영관 101", professor3, 35);

        timetableRepository.save(timetable1);
        timetableRepository.save(timetable2);
        timetableRepository.save(timetable3);
        timetableRepository.save(timetable4);
    }
}