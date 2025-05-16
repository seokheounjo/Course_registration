package com.example.course_registration.controller.manage;

import com.example.course_registration.entity.Room;
import com.example.course_registration.repository.RoomRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/admin/rooms")
public class RoomManageController {

    private final RoomRepository repo;
    public RoomManageController(RoomRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public String list(Model model) {
        model.addAttribute("rooms", repo.findAll());
        return "manage/rooms";
    }

    @GetMapping("/add")
    public String addForm(Model model) {
        model.addAttribute("room", new Room());
        return "manage/room_form";
    }

    @PostMapping("/add")
    public String addSubmit(Room room) {
        repo.save(room);
        return "redirect:/admin/rooms";
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        Room r = repo.findById(id).orElseThrow();
        model.addAttribute("room", r);
        return "manage/room_form";
    }

    @PostMapping("/edit/{id}")
    public String editSubmit(@PathVariable Long id, Room room) {
        room.setId(id);
        repo.save(room);
        return "redirect:/admin/rooms";
    }

    @GetMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        repo.deleteById(id);
        return "redirect:/admin/rooms";
    }
}
