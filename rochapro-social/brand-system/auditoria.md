# Auditoria de origem — 10/11/2026

## Identidade encontrada

`assets/identidade-visual/README.md`, `02-identidade/cores.json`, `tokens.css`, `tipografia.md`, `guia-de-uso.md` e `brand.css` fixam vermelho #E10606, preto #080808, cinza #D9D9D9 e branco #FFFFFF. Montserrat é a família sugerida, sem arquivo de fonte incluído. Grafismos existentes: diagonais e rastros de pneu. O arco superior do R permanece liso; apenas as pernas inferiores recebem textura.

As versões horizontal e vertical, clara e escura, monocromáticas e símbolo R estão em `01-marca/`; PNGs transparentes estão em `05-exportacoes/logos-png-transparentes/`. O README declara que são aproximações vetoriais preliminares do painel aprovado, não matrizes oficiais finais. A entrega preserva esses arquivos, sem alegar que sejam versões homologadas. Não foi localizada outra matriz oficial no repositório.

O painel `00-referencias/painel-identidade-atual.png` é referência de marca; seus contatos ilustrativos não foram usados. A assinatura pública adotada é @rochaproauto, fornecida no briefing.

## Produtos e fotografias

Foram encontrados 95 diretórios e 700 JPGs em `assets/img/Fotos dos Kits/`, além de derivados em `assets/catalogo/` e `private/fotos/`. Este é o acervo de produtos disponível no projeto associado à Borrachas Rocha. Não foi encontrado acervo adicional de veículos com licença documentada nem manual de montagem homologado.

`data/catalogo-publico.js` contém o cadastro ativo derivado. `private/mapeamento-fotos.csv` relaciona fotos e códigos. `private/expedicao.html` conserva a composição importada da coluna N da planilha de kits; `docs/auditoria-dados.md` registra a importação. Os XLS originais não foram encontrados dentro do repositório nesta auditoria. Não se afirmou leitura direta de planilhas ausentes.

O cadastro derivado possui 437 produtos ativos, dos quais 91 têm fotos vinculadas, conforme auditoria existente e verificação do JSON. Registros sem foto, com aplicação contraditória ou composição pendente não foram escolhidos para estes conceitos.

## Escolha validada para os conceitos B e C

| Campo | Evidência |
| --- | --- |
| Código | KIT10006, encontrado no catálogo público ativo |
| Nome | Kit Bieleta Dianteira Blazer / S10 |
| Aplicação descrita | S10 e Blazer: 1995 a 2011 |
| Quantidade | 02 bieletas na descrição pública; quantidade corroborada pela ficha interna, linha 7 da planilha importada |
| Material | Borracha de pneu lonado, texto explícito da descrição |
| Foto B | Pasta 6 / Borrachas-277.jpg, 3062 × 3062 |
| Foto C | Pasta 6 / Borrachas-276.jpg, 3062 × 3062 |
| Vínculo | Pasta 6 → KIT10006 no mapeamento existente |

As fotos mostram duas unidades, compatíveis visualmente com a quantidade declarada. A identificação individual de cada ferragem não é inferida. O detalhe em C amplia o mesmo ponto da foto; não adiciona peça, medida, tolerância ou orientação de montagem.

## Reutilização e limites

Marcas e fotos são arquivos fornecidos no projeto e reutilizados no escopo autorizado pelo usuário. Não há licença ou cessão fotográfica formal anexada para auditoria jurídica independente. Não foram buscadas ou copiadas fotos de anúncios de terceiros. O cenário institucional foi gerado por ImageGen; o prompt completo está em `assets/automotive-hero-prompt.txt`. Não foram gerados produtos de catálogo.

`assets/hero-suspensao.webp` já existe no site, mas não comprova a instalação do KIT10006 e por isso não foi usado como evidência técnica. A fonte Montserrat veio do repositório oficial Google Fonts; o binário fica fora do pacote, em `.tmp`, respeitando o guia da identidade.

Os preços, saldos, localizações e códigos internos dos componentes não foram copiados para os materiais de campanha. A aplicação é apresentada como cadastrada e acompanhada de convite à confirmação; não se promete estoque, desconto, prazo, garantia ou certificação.
