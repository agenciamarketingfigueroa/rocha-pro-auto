"""Encode approved vehicle cover masters into the site's responsive WebP sizes.

Only resizes approved images from output/imagegen/blog-covers. Never substitutes
catalog photographs as covers.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / 'output/imagegen/blog-covers'
for model in ['l200', 'ranger', 's10', 'd20', 'f1000']:
    with Image.open(MASTERS / f'{model}-hero.png') as image:
        image = image.convert('RGB')
        for width, suffix in [(1672, ''), (1200, '-1200'), (800, '-800')]:
            height = round(width * 941 / 1672)
            image.resize((width, height), Image.Resampling.LANCZOS).save(
                ROOT / f'assets/site/{model}-hero{suffix}.webp',
                'WEBP', quality=88, method=6,
            )
print('Exported 5 vehicle covers in 3 responsive sizes.')
