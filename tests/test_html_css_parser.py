import pytest
from app.parsers.css_parser import CSSParser
from app.parsers.html_parser import HTMLParser


def test_html_parser():
    html_code = '''<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles/main.css">
    <script src="js/app.js"></script>
</head>
<body>
    <div id="app-root">
        <form action="/api/login" method="POST">
            <input type="text" name="username" />
        </form>
    </div>
</body>
</html>
'''
    parser = HTMLParser()
    result = parser.parse(html_code, "index.html")

    assert result.language == "HTML"
    assert len(result.imports) == 2
    assert result.is_entry_point is True
    assert any(s.name == "form:/api/login" for s in result.symbols)
    assert any(s.name == "app-root" for s in result.symbols)


def test_css_parser():
    css_code = '''@import url("theme.css");

:root {
    --primary-color: #3b82f6;
    --background-dark: #0f172a;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.container {
    background-color: var(--background-dark);
}
'''
    parser = CSSParser()
    result = parser.parse(css_code, "styles/global.css")

    assert result.language == "CSS"
    assert len(result.imports) == 1
    assert any(s.name == "--primary-color" for s in result.symbols)
    assert any(s.name == "fadeIn" for s in result.symbols)
