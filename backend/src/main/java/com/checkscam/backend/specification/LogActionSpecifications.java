package com.checkscam.backend.specification;

import com.checkscam.backend.dto.LogActionFilterRequest;
import com.checkscam.backend.entity.LogAction;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.jpa.domain.Specification;

import java.util.ArrayList;
import java.util.List;

public class LogActionSpecifications {

    public static Specification<LogAction> build(LogActionFilterRequest req) {
        return (root, query, cb) -> {

            List<Predicate> predicates = new ArrayList<>();

            if (req.getAccountId() != null) {
                predicates.add(cb.equal(root.get("account").get("id"), req.getAccountId()));
            }

            if (req.getTargetType() != null && !req.getTargetType().isBlank()) {
                predicates.add(cb.equal(root.get("targetType").get("name"), req.getTargetType()));
            }

            if (req.getAction() != null && !req.getAction().isBlank()) {
                predicates.add(
                        cb.like(
                                cb.lower(root.get("action")),
                                "%" + req.getAction().toLowerCase() + "%"));
            }

            if (req.getFrom() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("createdAt"), req.getFrom()));
            }

            if (req.getTo() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("createdAt"), req.getTo()));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}
