import pytest
from app.parsers.rust_parser import RustParser


def test_rust_parser_structs_traits_and_fn():
    code = """
use std::collections::HashMap;
use crate::models::{User, Account};

pub trait Authenticatable {
    fn authenticate(&self, token: &str) -> bool;
}

pub struct AuthService {
    tokens: HashMap<String, User>,
}

impl AuthService {
    pub async fn login(&self, email: &str) -> Result<String, Error> {
        Ok("token_123".to_string())
    }
}
"""
    parser = RustParser()
    res = parser.parse(code, "auth.rs")

    assert res.language == "Rust"
    assert len(res.classes) == 2
    class_names = [c.name for c in res.classes]
    assert "Authenticatable" in class_names
    assert "AuthService" in class_names
    assert len(res.functions) >= 1
    assert len(res.imports) >= 2
