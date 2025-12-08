package com.checkscam.backend.controller;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.service.AccountService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.data.domain.Page;

@RestController
@RequestMapping("/api/account")
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    // LIST (ADMIN)
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Page<AccountListDTO>> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        return ResponseEntity.ok(accountService.getAccounts(page, size));
    }

    // DETAIL (ADMIN + CTV)
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<AccountDetailDTO> getDetail(@PathVariable int id) {
        return ResponseEntity.ok(accountService.getByIdDTO(id));
    }

    // CREATE (ADMIN)
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<AccountDetailDTO> create(@RequestBody AccountCreateDTO dto) {
        return ResponseEntity.ok(accountService.create(dto));
    }

    // UPDATE (ADMIN)
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<AccountDetailDTO> update(
            @PathVariable int id,
            @RequestBody AccountUpdateDTO dto) {
        return ResponseEntity.ok(accountService.updateAccount(id, dto));
    }

    // DELETE (ADMIN)
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> delete(@PathVariable int id) {
        accountService.delete(id);
        return ResponseEntity.ok("Deleted");
    }

    // LOCK / UNLOCK
    @PutMapping("/{id}/lock")
    @PreAuthorize("hasRole('ADMIN')")
    public void lock(@PathVariable int id) {
        accountService.lock(id);
    }

    @PutMapping("/{id}/unlock")
    @PreAuthorize("hasRole('ADMIN')")
    public void unlock(@PathVariable int id) {
        accountService.unlock(id);
    }

    // ASSIGN ROLE
    @PutMapping("/{id}/assign-role")
    @PreAuthorize("hasRole('ADMIN')")
    public void assignRole(
            @PathVariable int id,
            @RequestParam String role) {
        accountService.assignRole(id, role);
    }

    // TOGGLE STATUS
    @PutMapping("/{id}/toggle-status")
    @PreAuthorize("hasRole('ADMIN')")
    public void toggle(@PathVariable int id) {
        accountService.toggleStatus(id);
    }
}
