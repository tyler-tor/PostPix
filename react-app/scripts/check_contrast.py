# WCAG 2.x contrast check of the design tokens (parses tokens.css). Prints pass/fail for AA (4.5 text, 3.0 UI/large).
import re, sys, os
# usage: python3 scripts/check_contrast.py  (run from react-app/)
HERE = os.path.dirname(os.path.abspath(__file__))
css = open(os.path.join(HERE, '..', 'src', 'styles', 'tokens.css')).read()
def vars_in(block):
    return {m.group(1): m.group(2) for m in re.finditer(r'--([\w-]+):\s*(#[0-9a-fA-F]{6})\b', block)}
light_block = css.split('@media (prefers-color-scheme: dark)')[0]
dark_block = css.split('@media (prefers-color-scheme: dark)')[1]
light = vars_in(light_block); dark = {**light, **vars_in(dark_block)}
def lum(h):
    r, g, b = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
PAIRS = [  # (fg, bg, need, what)
 ('ink','bg',4.5,'body text on page'), ('ink','surface',4.5,'body text on cards'), ('ink-2','bg',4.5,'secondary text on page'),
 ('ink-2','surface',4.5,'secondary text on cards'), ('ink-2','surface-2',4.5,'secondary text on hover/skeleton'),
 ('ink','surface-2',4.5,'text on hover bg'),
 ('accent','bg',4.5,'teal link text on page'), ('accent','surface',4.5,'teal text on cards'),
 ('accent-strong','surface',4.5,'strong teal text on cards'), ('accent-strong','accent-soft',4.5,'strong teal on soft tint'),
 ('on-accent','accent',4.5,'button text'), ('on-accent','accent-strong',4.5,'button text hover'),
 ('danger','danger-soft',4.5,'error text on tint'), ('danger','surface',4.5,'danger text on cards'),
 ('line-strong','surface',3.0,'input border vs card (UI 3:1)'), ('line-strong','bg',3.0,'input border vs page'),
 ('focus','bg',3.0,'focus ring vs page'), ('focus','surface',3.0,'focus ring vs card'),
 ('like','surface',3.0,'heart icon on card (UI 3:1)'), ('like','photo-bg',3.0,'heart on dark photo bg'),
 ('accent','surface',3.0,'accent as UI colour'),
 ('ink','accent-soft',4.5,'demo notice text'), ('accent-strong','accent-soft',3.0,'demo notice icon (UI 3:1)'),
]
bad = 0
for mode, pal in (('light', light), ('dark', dark)):
    print(f'-- {mode}')
    for fg, bg, need, what in PAIRS:
        r = ratio(pal[fg], pal[bg]); ok = r >= need; bad += (not ok)
        print(f"  {'PASS' if ok else 'FAIL'} {r:5.2f} (need {need}) {fg} on {bg}: {what}")
# extra: white on brand-deep / brand-mid, #d4efea on brand-deep (login hero)
for fg, bg, need, what in [('#ffffff', light['brand-deep'], 4.5, 'login headline'), ('#d4efea', light['brand-deep'], 4.5, 'login subtext'), ('#7fe3d6', light['brand-deep'], 4.5, 'wordmark accent on deep')]:
    r = ratio(fg, bg); ok = r >= need; bad += (not ok); print(f"  {'PASS' if ok else 'FAIL'} {r:5.2f} (need {need}) {fg} on brand-deep: {what}")
print('failures:', bad); sys.exit(1 if bad else 0)
