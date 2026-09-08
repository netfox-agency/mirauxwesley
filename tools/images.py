#!/usr/bin/env python3
"""
Génère les déclinaisons responsives (AVIF + WebP) de assets/img/ et réécrit
les <img> des pages en <picture> avec srcset/sizes.

    python3 tools/images.py

Idempotent : relancer après avoir ajouté ou remplacé une photo.
Les fichiers sources sont les .webp « pleine taille » de assets/img/ ;
les déclinaisons vivent dans assets/img/r/.
"""
import os, re, sys, glob, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img')
OUT = os.path.join(IMG, 'r')
WIDTHS = [480, 768, 1100, 1600, 2000]

# largeur d'affichage selon le contexte, pour que le navigateur choisisse juste
SIZES = [
    ('shot--main',   '(max-width:1080px) 88vw, 40vw'),
    ('shot--detail', '(max-width:1080px) 42vw, 19vw'),
    ('frame--wide',  '(max-width:1240px) 92vw, 1112px'),
    ('frame--small', '(max-width:1080px) 40vw, 18vw'),
    ('frame',        '(max-width:1080px) 92vw, 48vw'),
    ('ba__',         '(max-width:1240px) 92vw, 1112px'),
    ('about__media', '(max-width:1080px) 88vw, 34vw'),
    ('gal__i',       '(max-width:760px) 46vw, (max-width:1080px) 30vw, 23vw'),
    ('hubrow__img',  '112px'),
    ('hubfeat__img', '(max-width:760px) 92vw, 46vw'),
    ('band__bg',     '100vw'),
    ('hero__bg',     '100vw'),
    ('scard__img',   '(max-width:640px) 92vw, (max-width:1080px) 46vw, 31vw'),
    ('quote__bg',    '100vw'),
    ('urgence__bg',  '100vw'),
]
DEFAULT_SIZES = '(max-width:1080px) 92vw, 48vw'


def derivatives(regen=True):
    if not regen and os.path.isdir(OUT):
        made = {}
        for src in sorted(glob.glob(os.path.join(IMG, '*.webp'))):
            name = os.path.splitext(os.path.basename(src))[0]
            ws = sorted(int(re.search(r'-(\d+)\.webp$', f).group(1))
                        for f in glob.glob(os.path.join(OUT, name + '-*.webp')))
            if ws:
                made[os.path.basename(src)] = [(w, 0) for w in ws]
        return made
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    made = {}
    for src in sorted(glob.glob(os.path.join(IMG, '*.webp'))):
        name = os.path.splitext(os.path.basename(src))[0]
        im = Image.open(src).convert('RGB')
        widths = sorted({w for w in WIDTHS if w < im.width} | {im.width})
        made[os.path.basename(src)] = []
        for w in widths:
            h = round(im.height * w / im.width)
            rs = im.resize((w, h), Image.LANCZOS)
            wp = os.path.join(OUT, f'{name}-{w}.webp')
            av = os.path.join(OUT, f'{name}-{w}.avif')
            rs.save(wp, 'WEBP', quality=76, method=6)
            rs.save(av, 'AVIF', quality=52, speed=4)
            made[os.path.basename(src)].append((w, h))
    return made


IMG_RE = re.compile(r'<img\b[^>]*?src="((?:\.\./)*)assets/img/([A-Za-z0-9@._-]+\.webp)"[^>]*?>', re.S)


def sizes_for(html, pos, tag=""):
    """Une classe portee par le <img> lui-meme fait autorite ; sinon on cherche
    la classe de contexte la plus proche en amont."""
    for key, val in SIZES:
        if key in tag:
            return val
    window = html[max(0, pos - 700):pos]
    best, best_at = DEFAULT_SIZES, -1
    for key, val in SIZES:
        at = window.rfind(key)
        if at > best_at:
            best, best_at = val, at
    return best


def rewrite(path, made):
    html = open(path).read()
    # on repart toujours du <img> nu : on déballe les <picture> déjà posés
    html = re.sub(r'<picture>\s*<source[^>]*>\s*<source[^>]*>\s*(<img\b.*?>)\s*</picture>',
                  r'\1', html, flags=re.S)
    # ...et on retire leurs srcset/sizes pour repartir d'un <img> propre
    html = re.sub(r'(<img\b[^>]*?)\s+srcset="[^"]*"', r'\1', html)
    html = re.sub(r'(<img\b[^>]*?)\s+sizes="[^"]*"', r'\1', html)
    out, last, n = [], 0, 0
    for m in IMG_RE.finditer(html):
        pre, fname = m.group(1), m.group(2)
        if fname not in made:
            continue
        tag = m.group(0)
        if 'assets/img/r/' in tag:
            continue
        base = fname[:-5]
        variants = made[fname]
        srcset_w = ', '.join(f'{pre}assets/img/r/{base}-{w}.webp {w}w' for w, _ in variants)
        srcset_a = ', '.join(f'{pre}assets/img/r/{base}-{w}.avif {w}w' for w, _ in variants)
        sz = sizes_for(html, m.start(), tag)
        newtag = re.sub(r'\ssizes="[^"]*"', '', tag)
        newtag = newtag.replace('<img', f'<img sizes="{sz}" srcset="{srcset_w}"', 1)
        pic = (f'<picture><source type="image/avif" sizes="{sz}" srcset="{srcset_a}">'
               f'<source type="image/webp" sizes="{sz}" srcset="{srcset_w}">'
               f'{newtag}</picture>')
        out.append(html[last:m.start()]); out.append(pic)
        last = m.end(); n += 1
    out.append(html[last:])
    open(path, 'w').write(''.join(out))
    return n


if __name__ == '__main__':
    regen = '--keep' not in sys.argv
    made = derivatives(regen)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    tot = sum(os.path.getsize(f) for f in glob.glob(os.path.join(OUT, '*')))
    print(f'{len(made)} sources -> {len(glob.glob(os.path.join(OUT, "*")))} fichiers '
          f'({tot/1e6:.1f} Mo dans assets/img/r/)')
    targets = args or ([os.path.join(ROOT, 'index.html')] +
               sorted(glob.glob(os.path.join(ROOT, '*', 'index.html'))) +
               sorted(glob.glob(os.path.join(ROOT, '*', '*', 'index.html'))))
    for page in targets:
        print(' ', os.path.relpath(page, ROOT), rewrite(page, made), '<picture>')
