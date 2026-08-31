import pytest
from app.parsers.sql_parser import SQLParser


def test_sql_parser_ddl():
    sql = """
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE VIEW active_users AS
SELECT * FROM users WHERE is_active = 1;
"""
    parser = SQLParser()
    res = parser.parse(sql, "schema.sql")

    assert res.language == "SQL"
    assert len(res.classes) == 3
    table_names = [c.name for c in res.classes]
    assert "users" in table_names
    assert "orders" in table_names
    assert "active_users" in table_names
    assert len(res.imports) >= 1
    assert res.imports[0].module_name == "users"
