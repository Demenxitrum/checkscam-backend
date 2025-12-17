package com.checkscam.backend.service;

import com.checkscam.backend.dto.*;
import org.springframework.data.domain.Page;

public interface AccountService {

    Page<AccountListDTO> getAccounts(int page, int size);

    AccountDetailDTO getByIdDTO(int id);

    AccountDetailDTO create(AccountCreateDTO dto);

    AccountDetailDTO updateAccount(int id, AccountUpdateDTO dto);

    void delete(int id);

    void lock(int id);

    void unlock(int id);

    void assignRole(int id, String role);

    void toggleStatus(int id);
}
