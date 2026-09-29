#!/usr/bin/env python3
"""Turn a claude.ai quiz artifact into a standalone "friends edition" page.

Usage:
  python3 build_friends.py <artifact.html> <out/index.html> "<home-screen name>"

<artifact.html> = the full HTML that `Artifact read` saves (tool-results/artifact-*.html).
The artifact's sync code already falls back to localStorage when window.claude is
missing, so the questions and app logic are left untouched; only the page shell
changes. Every patch is asserted, so a template change fails loudly instead of
shipping a half-patched page.
"""
import sys

src, out, short = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(src, encoding="utf-8").read()


def rep(old, new, required=True):
    global html
    n = html.count(old)
    if n == 0 and not required:
        return
    assert n == 1, f"expected exactly 1 match, found {n}: {old[:70]!r}"
    html = html.replace(old, new)


# 1. Head: proper charset, keep search engines out, allow "Add to Home Screen" as an app
rep('<meta charset=utf8>',
    '<meta charset="utf-8">'
    '<meta name="robots" content="noindex,nofollow">'
    '<meta name="apple-mobile-web-app-capable" content="yes">'
    '<meta name="mobile-web-app-capable" content="yes">'
    f'<meta name="apple-mobile-web-app-title" content="{short}">')

# 2. Disclaimer on the home screen, right above the "Real test format" note
rep('<p class="note"><strong>Real test format</strong>',
    '<p class="note"><strong>Unofficial practice questions.</strong> Written with AI help from the '
    'lecture slides by a classmate, not by the lecturers, so some may be wrong. Every question shows '
    'its slide number: check the slide when in doubt. Spotted a mistake? Screenshot it and send it to '
    'whoever shared this link. Your progress is saved in this browser only.</p>\n  '
    '<p class="note"><strong>Real test format</strong>')

# 3. "Save file" buttons: claude.ai's downloads capability doesn't exist here -> plain browser download
rep('if(!dl){msgEl.textContent="Saving files isn\'t available here. Use Copy instead.";return;}',
    'if(!dl){const a=document.createElement("a");'
    'a.href=URL.createObjectURL(new Blob([data],{type:"text/plain;charset=utf-8"}));'
    'a.download=name;document.body.appendChild(a);a.click();a.remove();'
    'msgEl.textContent="Saved "+name+".";return;}',
    required=False)

# 4. Friends without a VPN can't reach Claude
rep('Paste or upload it to Claude and ask', 'Paste it into an AI chatbot and ask', required=False)

assert 'noindex' in html and 'Unofficial practice questions' in html
open(out, "w", encoding="utf-8").write(html)
print(f"{out}: {len(html):,} bytes")
