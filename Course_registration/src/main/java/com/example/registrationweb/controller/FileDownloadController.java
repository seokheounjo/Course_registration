package com.example.registrationweb.controller;

import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Controller
public class FileDownloadController {

    @GetMapping("/download")
    public ResponseEntity<Resource> downloadFile(@RequestParam String file, HttpServletResponse response) throws IOException {
        // 백슬래시를 포워드 슬래시로 변환 (이중 안전장치)
        file = file.replace('\\', '/');

        // 파일 경로 확인
        Path filePath = Paths.get(file);
        if (!Files.exists(filePath)) {
            return ResponseEntity.notFound().build();
        }

        // 파일 리소스 생성
        Resource resource = new FileSystemResource(filePath.toFile());

        // 파일명 추출
        String filename = filePath.getFileName().toString();

        // 컨텐츠 타입 결정 (MIME 타입)
        String contentType;
        try {
            contentType = Files.probeContentType(filePath);
            if (contentType == null) {
                contentType = "application/octet-stream";
            }
        } catch (IOException ex) {
            contentType = "application/octet-stream";
        }

        // 응답 헤더 설정
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body(resource);
    }
}