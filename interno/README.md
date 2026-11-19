# Área interna online

A consulta em https://interno.rochaproauto.com.br usa o Worker rochapro-interno. Composições e fotos são arquivos estáticos vinculados ao Worker. Todas as requisições passam pelo login no servidor, inclusive as fotos: assets.run_worker_first deve permanecer true. Não é necessário ativar R2.

Os papéis admin e staff podem consultar todas as fichas nesta versão. As senhas ficam nos segredos ADMIN_PASSWORD e STAFF_PASSWORD da Cloudflare. SESSION_SECRET é uma chave aleatória de pelo menos 32 caracteres. Nunca grave esses valores no HTML, no código ou no Git. As sessões duram oito horas. A interface não exibe botão de saída. O login limita tentativas por IP a cinco por minuto.

## Preparar e publicar

Requer Node.js e Wrangler autenticado na conta Cloudflare do domínio. Execute na raiz:

1. Tenha private/expedicao.html e private/fotos/ neste computador. Gere-os com scripts/build_catalog.py e as planilhas originais quando for atualizar os dados.
2. Execute node scripts/prepare_interno.mjs. O comando usa o modelo atualizado e os dados já embutidos, copiando somente a consulta e fotos WebP para .tmp/interno-assets/. As planilhas não são necessárias para atualizar a interface.
3. Execute node --test interno/src/worker.test.mjs interno/src/purchase-core.test.mjs interno/src/purchase-ui.test.mjs.
4. Na primeira publicação, cadastre os três segredos no Worker pelo painel ou por wrangler secret bulk --config interno/wrangler.jsonc, fornecendo JSON por stdin. Não salve esse JSON em arquivos publicados.
5. Execute wrangler deploy --config interno/wrangler.jsonc. A configuração desativa workers.dev e URLs de prévia.
6. Confira que /, /expedicao.html e /fotos/NOME.webp redirecionam para /login sem sessão e que as duas senhas permitem consultar. /expedicao.html continua indisponível mesmo com sessão: a consulta é servida apenas por /.

As pastas private/ e .tmp/ são ignoradas pelo Git. Não as publique no GitHub Pages nem em hospedagem estática sem o Worker de autenticação. Para atualizar os kits ou fotos, prepare e publique uma nova versão.

## Logo e tela inicial do iPhone

O preparo copia as logos e ícones oficiais de assets/identidade-visual/01-marca para o pacote do Worker. Somente as rotas de marca explicitamente permitidas, /apple-touch-icon.png e /manifest.webmanifest ficam disponíveis antes do login. As fotos e composições continuam protegidas. As páginas de login e consulta incluem o ícone Apple de 180×180 e o manifesto com nome RochaPro e abertura independente do navegador. Não há cache offline dos dados internos.

## Ferramentas

- **Consulta**, em /consulta (também disponível na raiz): ficha dos kits e busca das composições por fornecedor.
- **Pedido de compra**, em /pedido-de-compra: busca por kit ou código do fornecedor. Adicionar um kit multiplica as quantidades de suas peças e soma códigos repetidos, separando unidades PC, PAR e KIT. Cada linha pode ser editada ou excluída. Anotações ambíguas exigem preencher código, quantidade e unidade ou excluir a linha antes de adicionar.

O pedido é um rascunho salvo no armazenamento local do navegador deste aparelho, sem histórico de compras no servidor. O botão Fazer pedido pelo WhatsApp abre uma mensagem para Tigrinho, da Borrachas Rocha, no número +55 31 97160-6904. A mensagem contém saudação informal e apenas os códigos do fornecedor, quantidades e unidades; não inclui códigos ou nomes dos kits. O operador revisa e envia no WhatsApp. Nenhuma mensagem é enviada automaticamente e o rascunho não é apagado ao abrir o WhatsApp.
