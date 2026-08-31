import pytest
from app.parsers.go_parser import GoParser


def test_go_parser_structs_and_methods():
    code = """
package server

import (
    "fmt"
    "net/http"
)

type Config struct {
    Port int
    Host string
}

type Router interface {
    Route(path string) http.Handler
}

func (c *Config) StartServer() error {
    fmt.Printf("Listening on %s:%d\\n", c.Host, c.Port)
    return nil
}

func HealthCheck(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
}
"""
    parser = GoParser()
    res = parser.parse(code, "server.go")

    assert res.language == "Go"
    assert len(res.classes) == 2
    assert res.classes[0].name == "Config"
    assert res.classes[1].name == "Router"
    assert len(res.functions) == 2
    assert res.functions[0].name == "StartServer"
    assert res.functions[1].name == "HealthCheck"
