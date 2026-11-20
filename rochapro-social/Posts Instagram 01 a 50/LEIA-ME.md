# Posts Instagram 01 a 50

Coleção da RochaPro Auto Peças: **50 posts**, sendo **3 artes aprovadas preservadas e 47 novas**, com legendas para todos.

## Arquivos

- **PNG/**: 50 imagens em 1080 × 1350 px, proporção 4:5.
- **JPG/**: as mesmas 50 artes em JPEG para publicação.
- **Posts Instagram 01 a 50.md**: legendas prontas para copiar, com CTA, hashtags e textos alternativos.
- **Posts Instagram 01 a 50.pdf**: capa + uma página por post, com prévia, legenda e orientações.
- **Previa.html**: galeria local com busca por modelo, kit ou tema, acesso aos arquivos e botão para copiar legendas. Abra com um navegador.
- **Previa/**: miniaturas e cinco folhas de contato para conferir a sequência.
- **Controle dos posts.csv**: controle de publicação, separado por ponto e vírgula, para abrir no Excel.
- **Fontes/**: conteúdo estruturado, layouts HTML/CSS, imagens utilizadas e scripts de exportação.

## Uso

1. Localize o número interno na galeria ou no controle.
2. Publique o JPG ou PNG correspondente, preservando o formato 4:5.
3. Copie somente o conteúdo de **Legenda** do Markdown/PDF. Ele já contém CTA e hashtags.
4. Se desejar, use o campo **Texto alternativo** na acessibilidade da publicação.
5. Atualize o controle com a data da publicação.

O link previsto para a bio é **https://rochaproauto.com.br/links**. As legendas dos conteúdos informativos direcionam ao blog; o destino específico aparece nos documentos.

A numeração de 01 a 50 aparece apenas nos nomes de arquivo, documentos e galeria. Os números que já existiam nas primeiras artes aprovadas indicam quantidade de peças ou chamadas técnicas; não são numeração de posts. As três imagens originais foram copiadas sem alteração.

## Direção visual e referências

Montserrat, preto, branco e vermelho, fotografia de peças, painéis industriais, ampliações de detalhes e veículos em ambientação. A sequência expande as linhas Automotive Hero, Industrial Product e Engineering View aprovadas. As fotos dos kits são reais; cenas de veículos e estrada são ilustrativas e reaproveitam o acervo visual do projeto. Recortes e ampliações não representam escala dimensional.

As aplicações e os códigos foram consultados no catálogo público local. `Fontes/assets/origens.json` registra as fotos de origem. Os conteúdos informativos adaptam os seis artigos existentes no blog. Menções de kits em conteúdos de viagem se referem à manutenção, sem prometer capacidade fora de estrada.

## Edição e exportação

No repositório original, execute em sequência:

```text
python "rochapro-social/Posts Instagram 01 a 50/Fontes/conteudo.py"
python "rochapro-social/Posts Instagram 01 a 50/Fontes/montar.py"
node "rochapro-social/Posts Instagram 01 a 50/Fontes/render.cjs"
python "rochapro-social/Posts Instagram 01 a 50/Fontes/documentos.py"
```

Dependências: Python com Pillow, ReportLab e pypdf; Node com Playwright e Sharp; Chrome. Os scripts usam as fontes e os caminhos de aplicativos disponíveis no ambiente Windows deste projeto. Os três primeiros exports continuam vinculados aos originais em `rochapro-social/posts`.

Nada foi publicado automaticamente nas redes sociais.
