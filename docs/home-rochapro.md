# Home RochaPro

Página inicial institucional e de descoberta, substituindo o aviso “Em breve”.

- Hero: **Kits e buchas para seguir em frente.** Apresentação da linha de buchas, bieletas, coxins e kits. A cena final mostra uma Pajero TR4 ao lado da picape e um caminhão na estrada à direita.
- Seleção de 30 modelos com busca por nome/marca e filtros de categoria. Os quatro modelos com páginas próprias levam a elas. Os outros 26 abrem o catálogo com busca e montadora preenchidas.
- Símbolos de 16 marcas, com links para as aplicações cadastradas.
- Apresentação da RochaPro em Contagem, MG, e fotografia real do KIT10006.
- Seção editorial com Transamazônica, uso severo, aplicação de peças e revisão do Troller.
- Atendimento por WhatsApp, navegação mobile e estados de busca sem resultado.

## Conteúdo e manutenção

`content/home.mjs` concentra modelos, marcas e destinos. `scripts/build_home.mjs` gera o `index.html` e verifica se cada modelo tem pelo menos uma aplicação no catálogo público. Artigos são vinculados ao conteúdo existente em `content/posts.mjs`.

O catálogo público foi incluído na publicação em `_config.yml`, pois é o destino das consultas por modelo e marca. Ele utiliza exclusivamente o arquivo público existente; filtros são `noindex,follow`, evitando tratá-los como novas landing pages indexáveis. As quatro páginas por modelo continuam indexáveis.

```text
node scripts/build_home.mjs
python scripts/test_public_pages.py
```

Para conferir a navegação em um servidor HTTP local:

```text
python -m http.server 4173 --bind 127.0.0.1
node scripts/test_home.cjs
```

O teste de navegador usa Playwright e Chrome no Windows. `HOME_PREVIEW_URL` permite indicar outro endereço de prévia. Verifica busca combinada, ausência de resultados, links de consulta, imagens, menu mobile e ausência de transbordamento em 1440, 390 e 320 px.

## Imagens e referências

Hero gerada com a ferramenta integrada `image_gen`, sem CLI. Exportada em WebP, com versões de 800, 1280 e 1920 px e imagem social 1200 × 630. Original: `exec-5b4d0e72-72bd-412a-a77c-973abffb42c5.png` no acervo de imagens geradas. Os arquivos utilizados estão em `assets/home/`.

Prompt final:

> Create a premium photographic website hero background for a Brazilian automotive parts brand, RochaPro. No text, no logos, no typography. Wide landscape 21:9 cinematic image, ideally 2520x1080. A quiet scenic paved mountain overlook in southeastern Brazil at golden hour turning to dusk, layered blue-grey mountains, warm thin band of sunset sky, dramatic natural light. On the RIGHT HALF only, a realistic silver midsize double cab pickup truck and slightly behind it a dark graphite compact everyday hatchback, stationary safely in a paved parking turnout, three-quarter rear / side angles facing toward the mountain road, restrained tasteful photography, no vehicle badges or readable plates. Vehicles are road-going ordinary vehicles, not lifted extreme offroad builds. Left 45 percent is mostly dark natural roadside and subdued mountain landscape, open negative space suitable for white text overlay. Horizonal composition with vehicles entirely within frame, moderate size rather than filling frame, photographic landscape remains dominant. Asphalt texture subtle, warm edge highlights on metal, natural colors, no red neon, no smoke, no people, no fake collage, no dashboard, no products, no decorations. Mood: welcoming, inspiring road trip, real everyday journeys, sophisticated automotive editorial photography, extremely polished. Keep dark bottom-left and upper-left, make central-right vehicles clear. This will be a full-width homepage background.

Fotos dos veículos e artigos reaproveitam o acervo ilustrativo do site. `pecas-reais.webp` é uma exportação da fotografia original `rochapro-social/assets/kit10006-277.jpg`.

Símbolos de montadoras: [Car Logos Dataset](https://github.com/filippofilip95/car-logos-dataset), com URLs individuais registradas em `assets/home/brands/sources.json`. Os símbolos identificam aplicações do catálogo, sem indicação de representação oficial das montadoras.

## Verificação

Metadados, dados estruturados, referências locais e links conferidos pelos testes públicos. Os 26 links para consultas filtradas retornaram produtos no navegador. Os quatro destinos com páginas próprias foram conferidos pelo teste de páginas públicas. Revisão visual feita em desktop e celular por capturas locais; a janela de prévia integrada estava indisponível.
