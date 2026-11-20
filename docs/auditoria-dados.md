# Auditoria dos dados e fotos

## Atualização de fotos — 20/11/2026

- Reprocessadas as pastas diretamente em `assets/img/Fotos dos Kits/`, respeitando os códigos corrigidos e sem alterar títulos, descrições ou composições dos cadastros existentes.
- 437 produtos ativos, dos quais 134 têm fotos (antes, 91). Foram geradas 1.002 imagens WebP para o catálogo e 1.002 para a consulta interna de 786 kits.
- 46 produtos ativos passaram a ter fotos, incluindo as oito imagens movidas de `KIT2393` para `KIT239`, correção confirmada pela equipe.
- `KIT234 (Conferir nome do kit)` permanece pendente, conforme solicitado. A pasta `KIT234`, sem observação, fornece cinco fotos ao kit 234.
- As pastas de lotes `10-11-2026` e `0. Kits-20261022T134400Z-1-001-comprimidas` não são reimportadas; usam-se as pastas organizadas no nível principal. Os kits 22, 173 e 216 perderam os vínculos anteriores por não terem pasta correspondente nesse nível. Há fotos identificadas como KIT10022 dentro do lote arquivado; elas permanecem lá, sem incorporação automática.
- As pastas dos códigos 967, 969, 970, 971, 991 e 992 continuam sem cadastro correspondente e não criam produtos automaticamente.
- Pastas específicas prevalecem sobre compartilhadas: `Kit 21` sobre `Kit 21 e 35`; `KIT59` e `KIT60` sobre `KIT60 (=KIT59)`. As duas pastas específicas existentes para cada um dos kits 88, 95 e 230 são mantidas, reunindo suas fotos.
- Observações como `(Foto com 2)` não são interpretadas como códigos. Todas as imagens e caminhos de arquivos públicos e internos foram conferidos; o pacote local da área interna também remove fotos antigas sem uso.

## Importação original — 22/10/2026

## Fontes recebidas

| Fonte | Registros | Uso |
| --- | ---: | --- |
| Lista de Produtos (Rocha Pro Auto).xls | 786 | Catálogo; 437 ativos e 349 inativos; substitui o CSV anterior |
| Planilha de Kits.xls | 785 códigos únicos | Consulta local da coluna C (código) e N (composição) |
| assets/img/Fotos dos Kits/ | 95 pastas, 700 fotos JPG | Vínculo por número no nome da pasta |

A importação preserva os arquivos originais. O XLS novo tem os mesmos códigos e títulos do CSV anterior. O catálogo público contém apenas código, título, descrições adicionais disponíveis, classificações para filtros e imagens reduzidas de produtos ativos. Preços, saldos, localização, anotação de composição e a planilha bruta não entram no arquivo público.

## Resultado

- 437 produtos ativos pesquisáveis; 91 têm fotos de kit vinculadas e 346 estão com marcador de foto ausente.
- 19 produtos ativos têm descrição adicional útil no XLS; 418 permanecem apenas com o título. A busca e a classificação de montadora usam esses textos adicionais. Perguntas frequentes antigas com afirmações sobre estoque e garantia foram removidas da publicação.
- 785 kits têm registro no XLS; 83 desses não têm composição na coluna N.
- `KIT10972` existe no XLS de produtos, mas não no XLS de kits. A consulta local mostra o kit sem composição confirmada e uma anotação auxiliar da lista de produtos, explicitamente identificada como tal. Assim, há 84 fichas com composição pendente no conjunto consultável.
- As pastas `962` a `971` sugerem códigos `KIT10962` a `KIT10971`, ausentes dos dois arquivos de produtos. As fotos originais foram mantidas sem criar produtos ou composições por suposição.
- A pasta `21` prevalece para `KIT10021`; `21 e 35` permanece para `KIT10035`. `KIT 972` prevalece para `KIT10972`; `KIT 204 - 972` permanece para `KIT10204`. Regra confirmada pela equipe.
- A classificação de função usa palavras explícitas do título e permite mais de uma função no mesmo kit. A montadora também pode ser identificada na descrição adicional. Em 22 produtos ativos a montadora não pôde ser identificada. Em 136, a função não correspondeu com segurança a uma das funções pedidas e ficou em “Outras funções”. Não há produto ativo classificado como “Escapamento” nesta versão da lista.

O detalhamento das pastas e suas decisões de vínculo está em `private/mapeamento-fotos.csv` após executar o importador. Esse arquivo e `private/auditoria-importacao.json` permanecem locais. As 623 imagens derivadas públicas ocupam cerca de 10 MB; as imagens para consulta local ficam em `private/fotos/`.

## Conferência necessária na expedição

As anotações da coluna N misturam padrões de quantidade e unidade. A tela mostra o texto original e só calcula um total auxiliar quando um trecho apresenta `código: número unidade` de forma clara. Trechos como `5007: 04` ficam marcados para conferência. `PN`, `Pause` e `sob medida` são identificados como componentes de outra marca ou sob medida. Fotos de pastas de kits são fotos do conjunto, não fotografias individuais dos componentes.

Para preencher as 84 composições pendentes ou adicionar `KIT10962` a `KIT10971`, é necessária uma planilha atualizada ou uma confirmação manual da ficha técnica. Até lá, esses dados não são inferidos.
