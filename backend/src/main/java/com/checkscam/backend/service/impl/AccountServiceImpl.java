package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.entity.*;
import com.checkscam.backend.repository.*;
import com.checkscam.backend.service.AccountService;
import com.checkscam.backend.service.LogActionService;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AccountServiceImpl implements AccountService {

    private final AccountRepository accountRepo;
    private final AccountRoleRepository roleRepo;
    private final AccountStatusRepository statusRepo;
    private final LogActionService logService;

    private static final DateTimeFormatter F = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // =====================================================================
    // LIST + DETAIL
    // =====================================================================

    @Override
    public Page<AccountListDTO> getAccounts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Account> accounts = accountRepo.findAll(pageable);

        return accounts.map(a -> AccountListDTO.builder()
                .id(a.getId())
                .email(a.getEmail())
                .name(a.getName())
                .role(a.getRole().getName())
                .status(a.getStatus().getName())
                .build());
    }

    @Override
    public AccountDetailDTO getByIdDTO(int id) {
        Account acc = accountRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Account not found"));
        return toDetail(acc);
    }

    private AccountDetailDTO toDetail(Account a) {
        return AccountDetailDTO.builder()
                .id(a.getId())
                .email(a.getEmail())
                .name(a.getName())
                .role(a.getRole().getName())
                .status(a.getStatus().getName())
                .createdAt(a.getCreatedAt().format(F))
                .build();
    }

    // =====================================================================
    // CREATE + UPDATE
    // =====================================================================

    @Override
    public AccountDetailDTO create(AccountCreateDTO dto) {

        if (accountRepo.existsByEmail(dto.getEmail())) {
            throw new RuntimeException("Email already used.");
        }

        AccountRole role = roleRepo.findById(dto.getRoleId())
                .orElseThrow(() -> new RuntimeException("Role not found"));

        AccountStatus status = statusRepo.findById(1) // ACTIVE
                .orElseThrow();

        Account acc = Account.builder()
                .email(dto.getEmail())
                .name(dto.getName())
                .password(dto.getPassword()) // TODO: encrypt by BCrypt
                .role(role)
                .status(status)
                .build();

        Account saved = accountRepo.save(acc);
        logService.log(saved.getId(), "CREATE_ACCOUNT", "ACCOUNT", saved.getId());

        return toDetail(saved);
    }

    @Override
    public AccountDetailDTO updateAccount(int id, AccountUpdateDTO dto) {

        Account acc = accountRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Account not found"));

        if (dto.getName() != null)
            acc.setName(dto.getName());

        if (dto.getRoleId() != null) {
            AccountRole role = roleRepo.findById(dto.getRoleId())
                    .orElseThrow();
            acc.setRole(role);
        }

        if (dto.getStatusId() != null) {
            AccountStatus status = statusRepo.findById(dto.getStatusId())
                    .orElseThrow();
            acc.setStatus(status);
        }

        Account saved = accountRepo.save(acc);
        logService.log(saved.getId(), "UPDATE_ACCOUNT", "ACCOUNT", saved.getId());

        return toDetail(saved);
    }

    // =====================================================================
    // LOCK / UNLOCK / DELETE
    // =====================================================================

    @Override
    public void delete(int id) {
        accountRepo.deleteById(id);
        logService.log(id, "DELETE_ACCOUNT", "ACCOUNT", id);
    }

    @Override
    public void lock(int id) {
        Account a = accountRepo.findById(id).orElseThrow();
        AccountStatus locked = statusRepo.findById(2).orElseThrow();
        a.setStatus(locked);
        accountRepo.save(a);
        logService.log(id, "LOCK_ACCOUNT", "ACCOUNT", id);
    }

    @Override
    public void unlock(int id) {
        Account a = accountRepo.findById(id).orElseThrow();
        AccountStatus active = statusRepo.findById(1).orElseThrow();
        a.setStatus(active);
        accountRepo.save(a);
        logService.log(id, "UNLOCK_ACCOUNT", "ACCOUNT", id);
    }

    @Override
    public void assignRole(int id, String role) {
        Account a = accountRepo.findById(id).orElseThrow();
        AccountRole r = roleRepo.findByName(role).orElseThrow();
        a.setRole(r);
        accountRepo.save(a);

        logService.log(id, "ASSIGN_ROLE_" + role.toUpperCase(), "ACCOUNT", id);
    }

    @Override
    public void toggleStatus(int id) {
        Account a = accountRepo.findById(id).orElseThrow();

        AccountStatus active = statusRepo.findByName("ACTIVE").orElseThrow();
        AccountStatus inactive = statusRepo.findByName("INACTIVE").orElseThrow();

        if (a.getStatus().getName().equals("ACTIVE")) {
            a.setStatus(inactive);
            logService.log(id, "DEACTIVATE_ACCOUNT", "ACCOUNT", id);
        } else {
            a.setStatus(active);
            logService.log(id, "ACTIVATE_ACCOUNT", "ACCOUNT", id);
        }

        accountRepo.save(a);
    }
}
