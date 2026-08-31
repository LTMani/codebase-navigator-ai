import pytest
from app.parsers.java_parser import JavaParser


def test_java_parser_spring_service():
    code = """
package com.example.ecommerce.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

@Service
public class PaymentServiceImpl implements PaymentService {

    @Autowired
    private PaymentRepository paymentRepo;

    public Payment processPayment(Order order, Double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Invalid amount");
        }
        return paymentRepo.save(new Payment(order.getId(), amount));
    }
}
"""
    parser = JavaParser()
    res = parser.parse(code, "PaymentServiceImpl.java")

    assert res.language == "Java"
    assert len(res.classes) == 1
    assert res.classes[0].name == "PaymentServiceImpl"
    assert "PaymentService" in res.classes[0].base_classes
    assert len(res.functions) == 1
    assert res.functions[0].name == "processPayment"
    assert len(res.imports) == 3
