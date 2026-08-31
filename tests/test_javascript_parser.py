import pytest
from app.parsers.javascript_parser import JavaScriptParser


def test_javascript_parser_imports_and_functions():
    code = '''import React, { useState, useEffect } from 'react';
import { fetchUserData } from '../api/userApi';
const axios = require('axios');

export class UserDashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = { users: [] };
    }

    render() {
        return <div>Dashboard</div>;
    }
}

export const loadData = async (userId) => {
    if (!userId) {
        return null;
    }
    const res = await fetchUserData(userId);
    return res.data;
};

function formatName(first, last) {
    return `${first} ${last}`;
}
'''
    parser = JavaScriptParser()
    result = parser.parse(code, "components/UserDashboard.jsx")

    assert result.language == "JavaScript"
    assert len(result.imports) >= 3
    assert len(result.classes) == 1
    assert result.classes[0].name == "UserDashboard"

    assert len(result.functions) == 2
    fn_names = [f.name for f in result.functions]
    assert "loadData" in fn_names
    assert "formatName" in fn_names

    assert result.layer_hint == "presentation"
    assert result.metrics.total_lines > 0
