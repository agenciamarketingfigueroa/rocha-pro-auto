# RochaPro Auto Peças — catálogo e consulta local de kits

Este repositório contém um catálogo estático dos **produtos ativos** da lista fornecida e uma ficha de consulta de kits para uso **local na expedição**. A lista original tem campos comerciais e operacionais; somente código, título, descrição de produto disponível, função, montadora inferida dos textos e fotos reduzidas entram no site público.

Contagens, lacunas e decisões de vínculo de fotos: [auditoria dos dados](docs/auditoria-dados.md).

## Página inicial temporária

`index.html` exibe a página “Em breve” com o contato comercial. Até o lançamento, o GitHub Pages exclui `catalogo.html` da publicação por meio de `_config.yml`.

## Abrir o catálogo localmente

Abra `catalogo.html` no navegador ou sirva esta pasta com `python -m http.server 8000` e acesse `http://localhost:8000/catalogo.html`. A busca aceita código ou palavras do título e das descrições adicionais. Os filtros de montadora e função são combináveis, a URL preserva os filtros e o catálogo mostra 24 itens por vez.

O XLS de produtos tem descrições adicionais para **19 dos 437 produtos ativos** após remover duplicatas do título. Elas aparecem nas fichas e entram na busca e na inferência de montadoras; nos demais, o título continua sendo a única descrição disponível. Os trechos antigos de perguntas frequentes foram descartados porque continham promessas de estoque e garantia que podem estar desatualizadas.

O ícone de carrinho mostra a quantidade de peças. É possível aumentar ou diminuir quantidades, remover um produto e limpar todos os itens. O carrinho é salvo no armazenamento local do navegador e restaurado ao voltar ao catálogo no mesmo navegador. **Enviar pedido pelo WhatsApp** abre uma mensagem pronta para `+55 31 97358-9165`, número confirmado pela equipe; o cliente confere e envia no WhatsApp. O catálogo não cobra nem registra o pedido no servidor.

O banner usa a identidade visual em `assets/identidade-visual/` e uma imagem de fundo em `assets/hero-suspensao.webp`. Na grade, a área da foto é quadrada (1:1), exibe a peça inteira e deixa o nome do kit abaixo.

Montadora e função são classificações automáticas feitas a partir dos textos do produto, para facilitar a navegação. Um kit pode aparecer em mais de uma função quando seu título cita ambas. Elas não são uma ficha de aplicação homologada. Quando a montadora não pode ser reconhecida com segurança, o item continua disponível pela busca, pela função e pelo filtro “Montadora não identificada”. Confirme a aplicação antes da venda.

## Consultar kits na expedição

No catálogo aberto neste computador (`catalogo.html` ou `http://localhost:8000/catalogo.html`), clique em **Área interna** no menu. Também é possível abrir `private/expedicao.html` diretamente. O link no menu só aparece quando o catálogo está aberto via arquivo local ou `localhost`/`127.0.0.1`.

Se a tela abrir mas a busca nova não funcionar, atualize o arquivo local já gerado com `python scripts/refresh_expedicao.py` na raiz do projeto e reabra `private/expedicao.html`. Esse comando reaproveita os dados de kits embutidos no arquivo; não precisa das planilhas XLS. `expedicao/template.html` é apenas o modelo sem dados e mostra um aviso quando aberto diretamente. Se `private/expedicao.html` não existir, copie a pasta `private/` do computador em que a consulta foi gerada ou execute o importador com as planilhas originais.

Selecione **Código do kit** para consultar a ficha e informar a quantidade. A busca aceita o código completo ou o número abreviado: `89` vira `KIT10089`; `01`, `kit 1` e `kit01` viram `KIT10001`; `243` vira `KIT10243`. A ficha mostra o texto **original** da coluna N, fotos do kit quando existem e um cálculo auxiliar de quantidade somente para trechos no formato claro `código: quantidade unidade`. Trechos fora desse formato ficam marcados para conferência. `PN`, `Pause` e `sob medida` são sinalizados como itens de outra marca ou sob medida. Uma linha vazia exibe aviso de cadastro incompleto. Se a coluna N estiver vazia, uma eventual anotação da coluna `Cód. no fornecedor` da planilha de produtos aparece apenas como informação auxiliar para conferência. A ferramenta não altera estoque nem registra uma separação concluída.

Selecione **Código do fornecedor** e digite o código exato da peça para ver os kits que a usam na composição registrada da coluna N. A lista mostra a composição completa de cada kit, com as peças e quantidades originais por kit, destaca a peça pesquisada e permite abrir a ficha de cada kit. A busca reconhece códigos antes de `:`, códigos marcados com `PN` ou `Pause` e códigos isolados; ela não usa anotações auxiliares de kits sem composição confirmada. Códigos em formatos livres que não possam ser identificados com segurança exigem conferência na planilha original.

Em kits com composição, **Enviar peças pelo WhatsApp** abre uma mensagem para o mesmo número com código, quantidade de kits, peças com quantidades calculadas quando o formato permite e a composição original para conferência. Kits sem composição não exibem esse botão.

`private/` está no `.gitignore` porque a composição dos kits é informação interna. O arquivo local funciona **offline** e não tem autenticação por si só. Não publique `private/`, os arquivos CSV/XLS ou outras informações internas no GitHub Pages nem em hospedagem estática sem autenticação no servidor.

A área interna online está em `https://interno.rochaproauto.com.br`, servida por um Cloudflare Worker com login para administrador e equipe. As duas senhas ficam nos segredos do Worker. A consulta e as fotos são arquivos estáticos vinculados ao Worker, com autenticação obrigatória em todas as requisições (`run_worker_first: true`). Não é necessário ativar R2. Veja [o preparo da implantação e atualização](interno/README.md).

## Atualizar os dados

Requer Python 3.12+ e Pillow (`pip install Pillow`). Execute:

```text
python scripts/build_catalog.py "C:\caminho\Lista de Produtos (Rocha Pro Auto).xls" "C:\caminho\Planilha de Kits.xls"
python scripts/verify_build.py "C:\caminho\Lista de Produtos (Rocha Pro Auto).xls"
```

O primeiro comando lê os originais sem alterá-los e gera:

- `data/catalogo-publico.js` — somente campos públicos dos produtos ativos;
- `assets/catalogo/*.webp` — cópias leves das fotos dos produtos ativos;
- `private/fotos/*.webp` — cópias leves usadas somente na consulta local;
- `private/expedicao.html` — consulta offline com a composição original;
- `private/auditoria-importacao.json` e `private/mapeamento-fotos.csv` — contagens e vínculos de pastas de fotos para revisão interna.

As fotos originais em `assets/img/Fotos dos Kits/` permanecem no disco, mas são ignoradas pelo Git devido ao tamanho. Para atualizar fotos em outro computador, copie essa pasta localmente antes de executar a importação. O mapeamento lê as pastas diretamente dentro desse diretório: `KIT 1`, `KIT01` e `1` correspondem a `KIT10001`; `KIT 204 - 972` corresponde a `KIT10204` e `KIT10972`. Quando existe uma pasta específica com fotos para o código, ela prevalece sobre a compartilhada. Os demais códigos citados nas pastas compartilhadas continuam vinculados a elas. A auditoria registra esses casos.

Para trocar somente as fotos ou corrigir os códigos nos nomes das pastas, mantendo os cadastros e composições já importados:

```text
python scripts/refresh_photos.py
python scripts/verify_build.py
node scripts/build_tr4.mjs
node scripts/test_tr4.mjs
node scripts/prepare_interno.mjs
```

Esse fluxo requer os arquivos existentes em `data/` e `private/`, mas dispensa as planilhas. Regenera as imagens mesmo quando o original substituído tem data antiga, remove as cópias derivadas sem uso e atualiza os vínculos no catálogo e na consulta interna. Os títulos dos produtos continuam sendo os do cadastro; renomear uma pasta corrige o vínculo das fotos. Observações como `(Foto com 2)` não criam outro código. A indicação `(=KIT59)` é tratada como compartilhamento; pastas marcadas `Conferir` ficam pendentes. Pastas de lotes/datas e seus subdiretórios não são reimportados automaticamente. A preparação da área interna atualiza o pacote local; publicar continua sendo uma etapa separada, descrita em `interno/README.md`.

Quando apenas um kit mudou desde a última atualização completa, `python scripts/refresh_photos.py --kit KIT10239` regenera esse kit e reaproveita as demais imagens. O código deve ser completo; a opção pode ser repetida para vários kits.

## Limites conhecidos

- O XLS de kits tem composições vazias e anotações em formatos variados. A ficha preserva a anotação de origem, mas não atribui códigos nem quantidades a textos ambíguos.
- As fotos são vinculadas pelo nome das pastas informado pela equipe. Esse vínculo identifica o kit, não cada peça da composição. Não há fotos individuais das peças nesta importação.
- Não há checkout, preço, promessa de disponibilidade ou localização de estoque no catálogo público. O WhatsApp recebe somente um rascunho de pedido iniciado pelo cliente.

