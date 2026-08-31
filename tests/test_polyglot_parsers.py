import unittest
from app.parsers.parser_factory import ParserFactory

class TestPolyglotParsers(unittest.TestCase):
    def test_all_polyglot_parsers(self):
        samples = {
            'test.c': '#include <stdio.h>\nint main() { printf("hi"); return 0; }',
            'test.cpp': '#include <iostream>\nclass Engine { public: void run() {} };',
            'test.cs': 'using System;\nclass Program { static void Main() {} }',
            'test.kt': 'package com.demo\nfun main(args: Array<String>) { println("hi") }',
            'test.swift': 'import Foundation\nclass ViewController { func viewDidLoad() {} }',
            'test.php': '<?php\nfunction calculate($a, $b) { return $a + $b; }',
            'test.rb': 'require "json"\ndef process_data(item)\n  puts item\nend',
            'test.scala': 'package org.demo\nobject Main extends App { println("hi") }',
            'test.sh': '#!/bin/bash\nset -e\nfunction deploy() { echo "deploying"; }',
            'Dockerfile': 'FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nCMD ["python", "run.py"]',
            'test.tf': 'resource "aws_s3_bucket" "b" {\n  bucket = "my-tf-test-bucket"\n}',
            'test.proto': 'syntax = "proto3";\nservice Greeter { rpc SayHello (HelloRequest) returns (HelloReply); }',
            'test.graphql': 'type User {\n  id: ID!\n  name: String!\n}',
        }
        for filename, code in samples.items():
            parser = ParserFactory.get_parser(filename)
            res = parser.parse(code, filename)
            self.assertGreater(res.total_lines, 0)
            self.assertNotEqual(res.language, "")
            self.assertGreaterEqual(res.complexity.cyclomatic_complexity, 1)

if __name__ == '__main__':
    unittest.main()
