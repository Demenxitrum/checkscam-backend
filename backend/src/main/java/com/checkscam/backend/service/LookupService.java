package com.checkscam.backend.service;

import com.checkscam.backend.dto.LookupRequest;
import com.checkscam.backend.dto.LookupResponse;

public interface LookupService {

    LookupResponse lookupPhone(String value);

    LookupResponse lookupBank(String value);

    LookupResponse lookupURL(String value);

    LookupResponse lookupGeneric(LookupRequest req);
}
