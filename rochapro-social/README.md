# RochaPro — conceitos editoriais para Instagram

Entrega inicial de 10/11/2026: auditoria, sistema editorial, três conceitos completos e apresentação comparativa. A expansão para nove publicações está planejada em `brand-system/plano-nove-posts.md`, aguardando revisão dos conceitos conforme o briefing. Nenhuma publicação foi enviada ao Instagram.

Abra `previews/conceitos.html` para comparar ou `previews/tres-conceitos.png` para compartilhar a apresentação.

## Arquivos

- `posts/`: três PNGs sRGB 1080 × 1350, três JPGs de alta qualidade e três fontes HTML editáveis.
- `templates/editorial.css`: posições, tamanhos, cores e regras comuns de composição.
- `templates/render.cjs`: exportação reproduzível com Chromium, Playwright e Sharp.
- `captions/`: título, texto da arte, legenda, CTA, hashtags e texto alternativo de cada publicação.
- `assets/`: fotografias originais copiadas sem alteração, logos existentes e cenário gerado.
- `brand-system/`: auditoria, design, planejamento e registro da revisão visual.
- `manifest.json`: produtos, arquivos, procedência, hashes e limites de validação.

## Editar e exportar

Altere textos no HTML de cada post e posições na folha CSS. Fotografias são elementos separados e permanecem editáveis. A ampliação técnica é um recorte CSS da fotografia original. Não há texto incorporado ao cenário gerado. Os logos são os PNGs existentes, sem redesenho; os SVGs originais continuam em `../assets/identidade-visual/01-marca/`.

Use Montserrat instalada localmente ou baixe a fonte variável oficial para `../.tmp/Montserrat.ttf`. A fonte não é redistribuída neste pacote, conforme o guia existente. Referência: https://github.com/google/fonts/tree/main/ofl/montserrat (licença OFL). Sem a fonte, a fonte substituta muda a composição; a exportação exige Montserrat carregada.

Dependências: Node.js, `playwright` e `sharp`; Chrome instalado. Configure `CHROME_PATH` se o executável estiver em outro lugar. Em Linux, instale o Chromium gerenciado pelo Playwright ou indique o executável. Instale dependências no ambiente de produção gráfica, sem alterar o aplicativo principal.

```text
node rochapro-social/templates/render.cjs
```

No ambiente atual, os pacotes estão no runtime do Codex. Se `node` não estiver no PATH, use seu caminho completo e defina `NODE_PATH` para a pasta `node_modules` desse runtime. O renderizador não acessa a rede e não publica arquivos. Ele atualiza PNG, JPG, miniaturas e apresentação após as edições.

## Escopo técnico

KIT10006: produto ativo no catálogo local; descrição indica duas bieletas dianteiras para S10/Blazer 1995–2011, de borracha de pneu lonado. A quantidade foi confrontada com a ficha interna, sem exportar códigos de componentes internos. A fotografia corresponde à pasta 6 pelo mapeamento do projeto. Não se trata de nova homologação técnica de aplicação.

O cenário de Automotive Hero foi gerado pela ferramenta nativa ImageGen para uso institucional. Não serve como prova de compatibilidade, fotografia documental ou desenho mecânico. Engineering View apresenta material e detalhe real; não representa instalação ou vista explodida.

O repositório classifica os arquivos da marca como preliminares. Foram reutilizados fielmente. O acervo fotográfico foi disponibilizado para este trabalho, mas não contém documentação de licença/autoria que permita certificar direitos além dessa autorização de uso no projeto.
