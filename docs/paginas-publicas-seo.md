# Páginas por modelo, links e blog — 20/11/2026

## Entrega

| Rota | Conteúdo |
| --- | --- |
| `/troller/` | 7 kits, 1 com fotografia; estabilizadora, Panhard, braços tensores e amortecedor |
| `/hilux/` | 21 kits, 8 com fotografia; seleção da picape, sem os 5 cadastros exclusivos da SW4 |
| `/frontier/` | 22 kits, 14 com fotografia; aplicação por geração, posição e medida |
| `/links/` | Cartão digital para as redes sociais, acessível pelo endereço direto, sem links na navegação interna e com `noindex,follow` |
| `/blog/` | Seis artigos com filtros por modelo e assunto |

Não foram criados preços, percentuais de desconto, estoque, promessas de desempenho, avaliações ou aplicações novas. A campanha da TR4 continua no fluxo existente; as três páginas novas usam conteúdo permanente. As imagens dos produtos vêm exclusivamente do catálogo público. Cenas dos veículos e da estrada são ilustrativas e estão identificadas como tal.

Cada artigo termina com uma seleção de kits e links para suas âncoras nas páginas de modelo. Os códigos são validados durante a geração. O tema da Transamazônica distingue condição da estrada, manutenção e modificação do veículo; não afirma que a maioria dos carros da região precisa de adaptação. O comunicado do DNIT é identificado como ocorrência histórica, não como condição atual da via. Fontes primárias são citadas junto às informações e novamente nas referências dos artigos.

## Edição e geração

- `content/models.mjs`: seleção dos modelos e textos das páginas. A Hilux inclui um cadastro compartilhado Hilux / SW4, mas exclui os que são exclusivamente SW4.
- `content/posts.mjs`: artigos, fontes, datas e kits relacionados. Atualize `updated` ao alterar o conteúdo de um artigo.
- `scripts/build_public_pages.mjs`: HTML estático, dados públicos de cotação, metadados, sitemap e RSS. Atualize `publicUpdated` quando houver alteração real nas páginas gerenciadas; não use a data de execução como atualização automática.
- `assets/site/`: estilo compartilhado, filtros, cotação e imagens. A identidade e a fonte local da TR4 são reaproveitadas.
- [Prompts e arquivos das imagens](imagens-modelos-blog.md): ferramenta integrada de geração de imagens, sem modificação das fotografias dos kits.

```text
node scripts/build_tr4.mjs
node scripts/build_public_pages.mjs
node scripts/test_tr4.mjs
node scripts/test_public_pages.mjs
python -m unittest discover -s scripts -p test_public_pages.py
```

A cotação usa o WhatsApp comercial `(31) 97358-9165`. A seleção fica separada por modelo no armazenamento da sessão; filtros não apagam itens selecionados. Os links individuais continuam funcionando sem JavaScript. Compartilhar um artigo abre um rascunho de mensagem; nada é enviado automaticamente.

## SEO implementado

- HTML com conteúdo completo, links rastreáveis e uma única H1 por página, disponível sem JavaScript.
- Títulos e descrições exclusivos, idioma `pt-BR`, URL canônica HTTPS com barra final e metadados Open Graph/Twitter.
- JSON-LD `Organization`, `WebSite`, `CollectionPage`, `ItemList` e `BreadcrumbList`; `BlogPosting` com autor institucional, editor, imagem, datas com fuso de Brasília e URL canônica nos artigos.
- Sem marcação de ofertas, estoque, avaliações ou preços fictícios. As páginas de modelo são coleções; a implementação não promete resultados enriquecidos de produto.
- `sitemap.xml` com 12 URLs indexáveis, datas explícitas de modificação e imagens reais das páginas. `/links/` fica fora do sitemap e recebe `noindex,follow`; permanece acessível aos robôs para que leiam essa instrução, conforme a [documentação do Google sobre noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing). `robots.txt` referencia o sitemap e mantém imagens/CSS/JS públicos acessíveis.
- RSS em `/blog/feed.xml`, navegação entre os modelos, links pela página inicial e ligação de cada artigo com os kits relacionados. A TR4 recebeu âncoras de kits e navegação para as novas páginas.
- Capas WebP em tamanhos de 800, 1200 e 1672 px, `srcset`, dimensões explícitas, carregamento tardio abaixo da primeira tela e prioridade da imagem principal. Fonte local com `font-display: swap`, sem dependência de CDN em tempo de execução.
- Os fontes editoriais e scripts de geração são excluídos do build do GitHub Pages. O catálogo geral continua fora da publicação, conforme configuração existente.

Referências de implementação: [Google — artigos e dados estruturados](https://developers.google.com/search/docs/appearance/structured-data/article), [Google — construção e envio de sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) e [Google — requisitos de snippets de produto](https://developers.google.com/search/docs/appearance/structured-data/product-snippet).

## Verificação e publicação

Os testes cobrem os códigos esperados por modelo, filtros, busca, cotação múltipla, remoção, restauração, isolamento entre modelos, armazenamento indisponível e filtros do blog. A conferência de HTML valida arquivos, âncoras entre páginas, imagens, títulos, descrições, canônicas, JSON-LD, RSS, sitemap, ausência de campos privados e kits no final de todos os artigos. A validação da TR4 continua passando.

A prévia visual foi bloqueada pela ferramenta de uso do computador: não foi possível determinar o endereço atual do Chrome com segurança. Por isso, renderização desktop/mobile e métricas reais de Core Web Vitals não foram verificadas. Os layouts possuem regras responsivas, mas a inspeção visual permanece pendente.

Os arquivos estão preparados localmente. Depois da publicação pelo fluxo existente do GitHub Pages, cadastrar ou usar a propriedade `https://rochaproauto.com.br/` no Google Search Console, enviar `https://rochaproauto.com.br/sitemap.xml` e inspecionar as páginas principais. A conta/propriedade não foi acessada nesta tarefa; não há confirmação de envio ou indexação. Validar também as URLs publicadas no Rich Results Test e PageSpeed Insights. SEO técnico facilita rastreamento e interpretação; não garante posição nos resultados.
