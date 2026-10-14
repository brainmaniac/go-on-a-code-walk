"""Fill and check representative offline reports; no reviewed-project code runs."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

TEMPLATE = Path(__file__).resolve().parents[1] / 'assets/report-template.html'
HOSTILE = '<script>alert("MR")</script> & </code><img src="https://bad.test/x"> \'quote\''
CODE = {
    'ESCAPED_CODE_1': 'order, err := accept(r)\nif err != nil {\n    http.Error(w, "invalid order", 400)\n    return\n}\ngo deliver(order)',
    'ESCAPED_CODE_2': 'func deliver(order Order) {\n    note := `' + HOSTILE + '`\n    if err := sendReceipt(order, note); err != nil {\n        log.Print(err)\n    }\n}',
    'ESCAPED_CODE_3': 'w.Header().Set("Content-Type", "application/json")\nif err := json.NewEncoder(w).Encode(order.ID); err != nil {\n    log.Print(err)\n}\nreturn',
    'ESCAPED_OLD_CODE': 'if err := deliver(order); err != nil {\n    http.Error(w, "delivery failed", 502)\n    return\n}\njson.NewEncoder(w).Encode(order.ID)',
}


class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], ''

    def all(self, tag=None):
        return [node for child in self.children
                for node in [child, *child.all()] if tag is None or node.tag == tag]

    def has_class(self, name):
        return name in self.attrs.get('class', '').split()

    def inside(self, tag):
        parent = self.parent
        while parent:
            if parent.tag == tag:
                return True
            parent = parent.parent
        return False


class ReportParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Element('document')
        self.feed(html)
        self.close()
        assert self.current is self.root, 'Unclosed element'

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {'meta', 'link', 'img', 'br', 'hr', 'input', 'source', 'wbr'}:
            self.current = node

    def handle_endtag(self, tag):
        assert self.current.tag == tag, f'Mismatched closing tag: {tag}'
        self.current = self.current.parent

    def handle_data(self, data):
        self.current.text += data


def filled_report(comparison=True, scenarios=1):
    html = TEMPLATE.read_text()
    if not comparison:
        html = re.sub(r'          <details class="old-code">.*?</details>\n', '', html, flags=re.S)
    # Both the ticket-link and no-ticket forms are supported by the skill.
    if scenarios == 1:
        html = re.sub(r'<a class="pill" href="{{JIRA_URL}}".*?</a>',
                      '<span class="pill">No ticket</span>', html)
        html = re.sub(r'        <ul class="checklist">.*?</ul>\n', '', html, flags=re.S)
    else:
        html = re.sub(r'        <p class="empty-note">.*?</p>\n', '', html)
        start = html.index('      <section class="walkthrough"')
        end = html.index('\n      <section class="section" aria-labelledby="findings-title"', start)
        scenario = html[start:end]
        copies = [scenario]
        for number in range(2, scenarios + 1):
            copy = re.sub(r'(id="|href="#|aria-labelledby=")([^"]+)"',
                          lambda m: f'{m[1]}{m[2]}-s{number}"', scenario)
            copy = copy.replace('{{SCENARIO_TITLE}}', 'Accept an order when receipt delivery fails')
            copy = copy.replace('{{SCENARIO_INPUT_AND_OUTCOME}}', 'The sender fails. The handler still acknowledges the accepted order, while the worker logs the delivery error.')
            copies.append(copy)
        entries = '<nav aria-label="Scenarios">' + ''.join(
            f'<a href="#path-1{suffix}">Scenario {i}</a> '
            for i, suffix in [(1, ''), *[(n, f'-s{n}') for n in range(2, scenarios + 1)]]) + '</nav>'
        html = html[:start] + entries + '\n'.join(copies) + html[end:]
    values = {
        'REPORT_LANG': 'en', 'PIPELINE_CLASS': 'unknown',
        'MR_TITLE': 'Queue a receipt after accepting a request',
        'SERVICE_INTRODUCTION': 'The receipt service accepts customer orders from the checkout API and returns an acknowledgement. It sends receipts in a background worker.',
        'TERM': 'Acknowledgement', 'TERM_DEFINITION': 'A response confirming that the order was accepted, before receipt delivery finishes.',
        'SCENARIO_TITLE': 'Accept an order and send its receipt',
        'SCENARIO_INPUT_AND_OUTCOME': 'A valid order produces an acknowledgement and a queued receipt.',
        'READING_ORDER_AND_CONCURRENCY': 'Read blocks 1, 2, 3. Block 2 runs concurrently with block 3; reading order is not execution order.',
        'BLOCK_1_TITLE': 'Accept the order and start delivery',
        'BLOCK_2_TITLE': 'Deliver the receipt in a goroutine',
        'BLOCK_3_TITLE': 'Return to the handler and acknowledge',
        'BRANCH_TRIGGER': 'Block 1 starts block 2 with go deliver(order).',
        'MAIN_RESUME_AND_WAIT': 'The handler continues to block 3 without waiting for delivery.',
        'BRANCH_CONCURRENCY_AND_JOIN': 'Delivery runs concurrently with the handler. There is no join.',
        'BRANCH_TRIGGER_AND_DATA': 'The accepted order is passed to the goroutine; the handler does not wait.',
        'BRANCH_COMPLETION_AND_MAIN_RETURN': 'The goroutine finishes independently. Resume reading the handler in block 3.',
        'RETURN_TO_CALLER_AND_RESPONSE': 'accept returns the order to the handler, which sends an acknowledgement.',
        'NEXT_LABEL': 'Next', 'BACK_TO_PATH_LABEL': 'Back to path',
        'SOURCE_REVISION': 'Remote source revision: source-sha',
        'MERGE_BASE_REVISION': 'Merge base: base-sha',
        'END_OF_WALK': 'The handler has returned. This scenario ends here.',
    }
    def fill(match):
        key = match[1]
        if key.startswith('ESCAPED_'):
            value = CODE[key]
        elif key.endswith('_URL'):
            revision = 'base-sha' if key == 'MERGE_BASE_SOURCE_URL' else 'source-sha'
            value = f'https://example.test/repo/blob/{revision}/handler.go#L12'
        else:
            value = values.get(key, key.replace('_', ' ').capitalize() + ': ' + HOSTILE)
        return escape(value, quote=True)
    return re.sub(r'{{([A-Z0-9_]+)}}', fill, html)


def check(html, scenarios, comparison):
    assert not re.search(r'{{[A-Z0-9_]+}}', html), 'Unfilled placeholder'
    nodes = ReportParser(html).root.all()
    ids = [n.attrs['id'] for n in nodes if 'id' in n.attrs]
    assert len(ids) == len(set(ids)), 'Duplicate ID'
    targets = {n.attrs['id']: n for n in nodes if 'id' in n.attrs}
    for node in nodes:
        assert node.tag not in {'script', 'link', 'img', 'iframe', 'object', 'embed', 'svg'}, 'Active or remote asset'
        for attr, value in node.attrs.items():
            assert not attr.startswith('on') and attr not in {'src', 'srcset', 'style'}, 'Active attribute'
            if attr == 'href':
                if value.startswith('#'):
                    assert value[1:] in targets, 'Missing fragment'
                    assert not targets[value[1:]].inside('details'), 'Collapsed fragment target'
                else:
                    assert urlsplit(value).scheme in {'http', 'https'}, 'Unsafe link'
            if attr in {'aria-labelledby', 'aria-describedby', 'aria-controls'}:
                assert all(ref in targets for ref in value.split()), 'Missing accessibility reference'
    assert next(n for n in nodes if n.tag == 'html').attrs.get('lang') == 'en'
    assert len([n for n in nodes if n.tag == 'main']) == 1
    for details in [n for n in nodes if n.tag == 'details']:
        assert details.children[0].tag == 'summary', 'Missing native summary'
    walks = [n for n in nodes if n.has_class('walkthrough')]
    assert len(walks) == scenarios
    for walk in walks:
        blocks = [n for n in walk.all('article') if n.has_class('story')]
        assert len(blocks) == 3
        path = next(n for n in walk.all('nav') if n.has_class('path'))
        path_links = {n.attrs.get('href') for n in path.all('a')}
        assert path_links == {'#' + n.attrs['id'] for n in blocks}, 'Incomplete path diagram'
        assert any(n.has_class('branch') for n in blocks), 'Missing async branch'
        for index, block in enumerate(blocks):
            assert not block.inside('details')
            current = next(n for n in block.all('pre') if not n.inside('details'))
            assert current.children[0].tag == 'code'
            assert current.children[0].text == CODE[f'ESCAPED_CODE_{index + 1}'], 'Code not escaped faithfully'
            assert not current.children[0].children, 'Injected code markup'
            source = next(n for n in block.all() if n.has_class('source-ref') and not n.inside('details'))
            assert 'source-sha' in source.all('a')[0].attrs['href'], 'Current code uses wrong revision'
            assert block.all('details'), 'Missing call explanation'
            links = block.all('a')
            back = [n for n in links if n.has_class('back-to-path')]
            assert len(back) == 1 and back[0].attrs['href'] == '#' + path.attrs['id']
            following = [n.attrs['href'] for n in links if n.has_class('next')]
            expected = ['#' + blocks[index + 1].attrs['id']] if index + 1 < len(blocks) else []
            assert following == expected, 'Wrong Next order'
    old = [n for n in nodes if n.has_class('old-code')]
    assert len(old) == (scenarios if comparison else 0)
    for details in old:
        assert 'base-sha' in details.all('a')[0].attrs['href'], 'Old code uses wrong revision'
        assert details.all('code')[0].text == CODE['ESCAPED_OLD_CODE'], 'Old code not escaped faithfully'
    css = next(n.text for n in nodes if n.tag == 'style')
    assert not re.search(r'@import|url\s*\(', css, re.I), 'Remote CSS asset'
    for rule in (':focus-visible', 'scroll-behavior: smooth', 'prefers-reduced-motion',
                 'scroll-behavior: auto', 'animation: none', 'transition: none'):
        assert rule in css, f'Missing accessibility style: {rule}'
    assert re.search(r'@media \(max-width: 760px\).*?\.path-lanes \{ grid-template-columns: 1fr;', css, re.S)


if __name__ == '__main__':
    with TemporaryDirectory(prefix='code-walk-check-') as directory:
        for scenarios in (1, 2):
            for comparison in (False, True):
                report = filled_report(comparison, scenarios)
                path = Path(directory) / f'report-{scenarios}-{comparison}.html'
                path.write_text(report)
                check(path.read_text(), scenarios, comparison)
        # Prove that navigation, escaping and offline failures are detected.
        report = filled_report()
        for broken in (report.replace('id="walk-2"', 'id="walk-1"'),
                       report.replace('href="#walk-2"', 'href="#missing"'),
                       report.replace('class="next" href="#walk-2"', 'class="next" href="#walk-3"'),
                       report.replace('&lt;script&gt;', '<script>'),
                       report.replace('</body>', '<script></script></body>')):
            try:
                check(broken, 1, True)
            except AssertionError:
                pass
            else:
                raise AssertionError('Invalid report passed')
    print('Passed: 4 filled reports and 5 invalid-report checks.')
