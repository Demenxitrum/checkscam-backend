package com.checkscam.backend.repository;

import com.checkscam.backend.entity.Report;
import com.checkscam.backend.entity.ReportType;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ReportRepository extends JpaRepository<Report, Integer> {

  // ===============================================
  // SUPPORT FOR LOOKUP MODULE (KHÔNG ĐƯỢC XÓA)
  // ===============================================
  @Query("""
      SELECT COUNT(r)
      FROM Report r
      WHERE r.type = :type AND r.infoValue = :value
      """)
  int countByTypeAndInfoValue(
      @Param("type") ReportType type,
      @Param("value") String value);

  // ================================
  // DASHBOARD: Đếm theo trạng thái
  // ================================
  long countByStatus_Id(Integer statusId);

  // ===============================================
  // DASHBOARD: Thống kê theo ngày
  // ===============================================
  @Query("""
      SELECT DATE(r.createdAt), COUNT(r)
      FROM Report r
      GROUP BY DATE(r.createdAt)
      ORDER BY DATE(r.createdAt) DESC
      """)
  List<Object[]> countReportsByDate();

  // ===============================================
  // DASHBOARD: Top value bị báo cáo nhiều nhất
  // ===============================================
  @Query("""
      SELECT r.infoValue, r.type.name, COUNT(r)
      FROM Report r
      GROUP BY r.infoValue, r.type.name
      ORDER BY COUNT(r) DESC
      """)
  List<Object[]> findTopReportedValues(Pageable pageable);

  // ===============================================
  // DASHBOARD: Thống kê số report theo từng loại
  // ===============================================
  @Query("""
      SELECT r.type.id, r.type.name, COUNT(r)
      FROM Report r
      GROUP BY r.type.id, r.type.name
      """)
  List<Object[]> countReportsByType();

  // ======================================================
  // ADMIN LOOKUP — REPORT ĐÃ DUYỆT (READ-ONLY)
  // ======================================================
  @Query("""
      SELECT r
      FROM Report r
      WHERE r.infoValue = :value
        AND UPPER(r.type.name) = UPPER(:typeName)
        AND UPPER(r.status.name) = 'APPROVED'
      """)
  List<Report> findApprovedByValueAndType(
      @Param("value") String value,
      @Param("typeName") String typeName);

  // ======================================================
  // ADMIN LOOKUP — ĐẾM REPORT THEO TRẠNG THÁI
  // ======================================================
  @Query("""
      SELECT COUNT(r)
      FROM Report r
      WHERE r.infoValue = :value
        AND UPPER(r.type.name) = UPPER(:typeName)
        AND UPPER(r.status.name) = UPPER(:statusName)
      """)
  int countByStatusAndValue(
      @Param("statusName") String statusName,
      @Param("typeName") String typeName,
      @Param("value") String value);

  // ======================================================
  // ADMIN LOOKUP — THỜI ĐIỂM BÁO CÁO ĐẦU TIÊN
  // ======================================================
  @Query("""
      SELECT MIN(r.createdAt)
      FROM Report r
      WHERE r.infoValue = :value
        AND UPPER(r.type.name) = UPPER(:typeName)
      """)
  LocalDateTime findFirstReportTime(
      @Param("typeName") String typeName,
      @Param("value") String value);

  // ======================================================
  // ADMIN LOOKUP — THỜI ĐIỂM BÁO CÁO GẦN NHẤT
  // ======================================================
  @Query("""
      SELECT MAX(r.createdAt)
      FROM Report r
      WHERE r.infoValue = :value
        AND UPPER(r.type.name) = UPPER(:typeName)
      """)
  LocalDateTime findLastReportTime(
      @Param("typeName") String typeName,
      @Param("value") String value);
}
