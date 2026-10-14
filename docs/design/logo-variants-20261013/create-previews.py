"""Generate original SVG logo explorations and a self-contained review page."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEAD = "M36 37V20L51 29Q64 24 77 29L92 20V37Q101 46 97 59Q91 73 64 74Q37 73 31 59Q27 46 36 37Z"


def svg(body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="{title}">
<title>{title}</title><g stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'''


def face(zen, color="white", y=0):
    eyes = ('<path d="M44 49Q50 55 56 49M72 49Q78 55 84 49" fill="none" '
            f'stroke="{color}" stroke-width="3.8"/>') if zen else (
                f'<g fill="{color}"><ellipse cx="50" cy="49" rx="3.5" ry="4.4"/>'
                '<ellipse cx="78" cy="49" rx="3.5" ry="4.4"/></g>')
    return f'<g transform="translate(0 {y})">{eyes}<path d="m61 60 3 2 3-2" fill="none" stroke="{color}" stroke-width="2.8"/></g>'


def quiet(zen):
    ink, accent = 'var(--ink,#3f51b5)', 'var(--accent,#673ab7)'
    if zen:
        body = f'''<path d="M50 70Q45 82 48 94H80Q83 82 78 70" fill="{ink}"/>
<path d="M49 79Q42 88 32 86M79 79Q86 88 96 86" fill="none" stroke="{ink}" stroke-width="6"/>
<path d="M50 90C36 81 23 88 27 99C32 112 51 110 64 100C77 110 96 112 101 99C105 88 92 81 78 90L64 97Z" fill="{accent}"/>
<path d="M40 99Q51 105 64 97Q77 105 88 99" fill="none" stroke="white" stroke-width="3"/>'''
    else:
        body = f'''<path d="M80 99C106 110 116 84 102 75" fill="none" stroke="{accent}" stroke-width="7"/>
<path d="M49 69Q42 82 44 104Q64 114 84 104Q86 82 79 69Z" fill="{ink}"/>
<path d="M54 91V104M74 91V104" fill="none" stroke="white" stroke-width="3"/>'''
    return body + f'<path d="{HEAD}" fill="{ink}"/>' + face(zen)


def loop(zen):
    ink, accent = 'var(--ink,#3f51b5)', 'var(--accent,#039be5)'
    ring = ('M41 98C14 87 7 51 25 28C43 5 76 7 96 25' if zen else
            'M78 101C110 107 121 74 106 56')
    body = ('M54 76Q49 85 41 87C30 92 40 104 53 98L64 91L75 98C88 104 98 92 87 87Q79 85 74 76' if zen else
            'M53 75Q47 85 47 101Q64 110 81 101Q81 85 75 75M56 90V103M72 90V103')
    head = 'M43 52V34L54 40Q64 36 74 40L85 34V52Q91 59 84 67Q77 75 64 75Q51 75 44 67Q37 59 43 52Z'
    eyes = 'M49 56Q53 60 57 56M71 56Q75 60 79 56' if zen else 'M53 54V58M75 54V58'
    return f'''<path d="{ring}" fill="none" stroke="{accent}" stroke-width="6.5"/>
<path d="{body}" fill="none" stroke="{ink}" stroke-width="5"/>
<path d="{head}" fill="white" stroke="{ink}" stroke-width="5"/>
<path d="{eyes}" fill="none" stroke="{ink}" stroke-width="3.2"/>
<path d="m62 65 2 1 2-1" fill="none" stroke="{ink}" stroke-width="2.4"/>'''


def merge(zen):
    ink, accent = 'var(--ink,#512da8)', 'var(--accent,#81d4fa)'
    if zen:
        body = '''<path d="M53 74Q48 83 41 85M75 74Q80 83 87 85" fill="none" stroke="white" stroke-width="6"/>
<path d="M51 86C36 78 29 91 39 98Q50 108 64 95Q78 108 89 98C99 91 92 78 77 86L64 94Z" fill="white"/>
<path d="M46 96Q54 101 64 94Q74 101 82 96" fill="none" stroke="var(--ink,#512da8)" stroke-width="2.8"/>'''
        branch = 'M88 91Q102 88 102 74V65'
        node = '<circle cx="102" cy="61" r="4"/>'
    else:
        body = '''<path d="M51 71Q46 85 48 102Q64 108 80 102Q82 85 77 71Z" fill="white"/>
<path d="M57 89V103M71 89V103" fill="none" stroke="var(--ink,#512da8)" stroke-width="3"/>'''
        branch = 'M82 96H90Q103 96 103 83V73M103 80Q94 80 94 69V64'
        node = '<circle cx="103" cy="69" r="3.8"/><circle cx="94" cy="60" r="3.8"/>'
    return f'''<rect x="9" y="9" width="110" height="110" rx="32" fill="{ink}"/>
<path d="{branch}" fill="none" stroke="{accent}" stroke-width="4.5"/>
<g fill="{accent}">{node}</g>{body}
<path d="{HEAD}" transform="translate(0 3) scale(1 .94)" fill="white"/>{face(zen, ink, -1)}'''


concepts = [
    ('01', 'quiet-cat', 'Quiet Cat', 'Simple silhouette. A seated cat settles into a clear lotus pose.', '#3f51b5', '#e8eaf6', quiet, 'Cleanest everyday mark'),
    ('02', 'zen-loop', 'Zen Loop', 'A lighter line icon. The tail opens into an ensō-inspired circle.', '#0277bd', '#e1f5fe', loop, 'Calmest, most minimal'),
    ('03', 'zen-merge', 'Zen Merge', 'A bold app icon. Git-like branches resolve into a calm, centered cat.', '#673ab7', '#ede7f6', merge, 'Strongest app identity'),
]

cards = []
for number, slug, name, description, color, surface, draw, positioning in concepts:
    for state in ('normal', 'zen'):
        (ROOT / f'{slug}-{state}.svg').write_text(svg(draw(state == 'zen'), f'{name} — {state} state'))
    cards.append(f'''<article style="--concept:{color};--surface:{surface}">
<div class="card-top"><span class="number">{number}</span><span class="position">{positioning}</span></div>
<div class="hero"><img src="{slug}-zen.svg" data-normal="{slug}-normal.svg" data-zen="{slug}-zen.svg" alt="{name} in meditation" /></div>
<h2>{name}</h2><p class="description">{description}</p>
<div class="states"><div><img src="{slug}-normal.svg" alt="Normal cat"/><span>Normal</span></div><svg width="40" height="24" viewBox="0 0 40 24" fill="none" stroke="#94a0b5" stroke-width="1.6"><path d="M5 12h28m-6-6 6 6-6 6"/></svg><div><img src="{slug}-zen.svg" alt="Zen cat"/><span>Zen</span></div></div>
<div class="app-preview"><img src="{slug}-zen.svg" alt=""/><span>GitHub Manager</span><span class="app-dot"></span></div>
<div class="size-preview"><span>Small-size check</span><img width="32" height="32" src="{slug}-zen.svg" alt="32 pixel preview"/><img width="24" height="24" src="{slug}-zen.svg" alt="24 pixel preview"/></div>
<button class="try" onclick="const card=this.closest('article');const normal=card.classList.toggle('normal');const icon=card.querySelector('.hero img');icon.src=icon.dataset[normal?'normal':'zen'];icon.alt='{name} — '+(normal?'normal':'zen');this.textContent=normal?'Enter zen mode':'Return to normal'">Return to normal</button>
</article>''')

html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>GitHub Manager — Three Zen Cat Concepts</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f8fc;color:#252139;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1760px;margin:auto;padding:66px 58px 38px}.eyebrow{font-size:13px;letter-spacing:.16em;color:#3f51b5;font-weight:650;text-transform:uppercase;margin:0 0 14px}header{display:flex;align-items:flex-end;justify-content:space-between;gap:35px;margin-bottom:42px}h1{font-size:48px;letter-spacing:-1.9px;line-height:1.12;margin:0;font-weight:700}header>p{max-width:390px;font-size:17px;line-height:1.65;color:#5e687d;margin:0}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px}article{background:white;border:1px solid #e0e6ef;border-radius:28px;padding:26px 32px 23px;box-shadow:0 10px 30px #303f9f05}.card-top{display:flex;justify-content:space-between;align-items:center;gap:10px}.number{font-size:14px;font-weight:650;color:var(--concept);background:var(--surface);padding:8px 12px;border-radius:11px}.position{color:#626c80;font-size:13px}.hero{height:274px;display:grid;place-items:center;margin:11px 0 3px}.hero>img{width:230px;height:230px;transition:opacity .25s,transform .35s}.normal .hero>img{transform:translateY(-3px)}h2{font-size:26px;letter-spacing:-.65px;margin:8px 0 10px}.description{font-size:16px;line-height:1.7;color:#5b667b;min-height:55px;margin:0}.states{display:flex;align-items:center;justify-content:center;gap:24px;padding:20px 0 22px}.states>div{display:grid;justify-items:center;gap:5px}.states img{width:68px;height:68px}.states span{font-size:12px;color:#647086}.app-preview{height:68px;display:flex;align-items:center;gap:10px;border:1px solid #e4e9f1;border-radius:14px;background:#fafbfe;padding:12px 17px}.app-preview>img{width:36px;height:36px}.app-preview>span:not(.app-dot){font-size:17px;font-weight:650;letter-spacing:-.35px}.app-dot{margin-left:auto;background:#66a18d;width:6px;height:6px;border-radius:50%}.size-preview{display:flex;align-items:center;gap:20px;height:62px}.size-preview>span{font-size:12px;color:#647086;margin-right:auto}.try{font:inherit;font-size:13px;color:var(--concept);border:1px solid #dce2ef;background:white;padding:9px 13px;border-radius:10px;cursor:pointer}.try:hover{background:var(--surface)}footer{display:flex;justify-content:space-between;margin-top:28px;color:#647086;font-size:13px;line-height:1.7}footer strong{color:#3f51b5;font-weight:550}@media(max-width:1000px){main{padding:35px 22px}header{display:block}header>p{margin-top:18px}section{grid-template-columns:1fr}h1{font-size:36px}article{max-width:560px;width:100%;margin:auto}.hero{height:240px}footer{display:block}}@media(prefers-reduced-motion:reduce){*{transition:none!important}}
'''
for _, slug, _, _, _, _, _, _ in concepts:
    html += f'article:has(img[src="{slug}-zen.svg"]){{--normal-image:url("{slug}-normal.svg")}}'
html += '''</style></head><body><main><header><div><p class="eyebrow">GitHub Manager · Logo exploration</p><h1>From Git to a quieter state.</h1></div><p>Three original cat marks, simplified for a clear header icon and a playful normal → zen transition.</p></header><section>'''
html += ''.join(cards)
html += '''</section><footer><span><strong>SVG concepts</strong> · Indigo, Deep Purple and Light Blue · Transparent assets</span><span>Review concepts only · Current app logo is unchanged</span></footer></main></body></html>'''
(ROOT / 'index.html').write_text(html)
print('Created six SVG states and the three-concept interactive review page.')
