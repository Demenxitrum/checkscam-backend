package com.checkscam.backend.service;

import com.checkscam.backend.dto.*;
import org.springframework.web.multipart.MultipartFile;

public interface ReportService {

    ReportResponseDTO create(ReportCreateRequest req, MultipartFile[] files);

    ReportListDTO getAll(int page, int size);

    ReportResponseDTO getDetail(Integer id);

    ReportResponseDTO approve(Integer id);

    ReportResponseDTO reject(Integer id);

    ReportResponseDTO update(Integer id, ReportUpdateRequest req);

    void delete(Integer id);
}
