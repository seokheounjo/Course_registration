@GetMapping
public String listStudents(Model model, HttpSession session) {
    // 로그인 확인 (관리자만 접근 가능)
    if (!"admin".equals(session.getAttribute("user"))) {
        return "redirect:/login";
    }

    // 가장 단순한 형태로 테스트
    try {
        List<Student> students = studentService.getAllStudents();
        model.addAttribute("students", students);
        model.addAttribute("totalItems", students.size());
        model.addAttribute("totalPages", 1);
        model.addAttribute("currentPage", 0);
        model.addAttribute("currentPageDisplay", 1);
        model.addAttribute("hasPrevious", false);
        model.addAttribute("hasNext", false);
        model.addAttribute("size", 20);
        model.addAttribute("sortBy", "name");
        model.addAttribute("sortDir", "asc");
        model.addAttribute("reverseSortDir", "desc");
        model.addAttribute("startItem", 1);
        model.addAttribute("endItem", students.size());
        
        return "admin/students/list";
    } catch (Exception e) {
        model.addAttribute("error", "Error: " + e.getMessage());
        return "error";
    }
}