package com.checkscam.backend.security;

import com.checkscam.backend.entity.Account;
import com.checkscam.backend.repository.AccountRepository;

import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

        private final AccountRepository accountRepo;

        @Override
        public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {

                Account acc = accountRepo.findByEmail(email)
                                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));

                return new User(
                                acc.getEmail(),
                                acc.getPassword(),
                                List.of(new SimpleGrantedAuthority("ROLE_" + acc.getRole().getName())));
        }
}
