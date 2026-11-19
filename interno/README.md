# Área interna online

A consulta em https://interno.rochaproauto.com.br usa o Worker rochapro-interno. Composições e fotos são arquivos estáticos vinculados ao Worker. Todas as requisições passam pelo login no servidor, inclusive as fotos: assets.run_worker_first deve permanecer true. Não é necessário ativar R2.

Os papéis admin e staff podem consultar todas as fichas nesta versão. As senhas ficam nos segredos ADMIN_PASSWORD e STAFF_PASSWORD da Cloudflare. SESSION_SECRET é uma chave aleatória de pelo menos 32 caracteres. Nunca grave esses valores no HTML, no código ou no Git. As sessões duram oito horas; Sair remove a sessão do navegador. O login limita tentativas por IP a cinco por minuto.

## Preparar e publicar

Requer Node.js e Wrangler autenticado na conta Cloudflare do domínio. Execute na raiz:

1. Tenha private/expedicao.html e private/fotos/ neste computador. Gere-os com scripts/build_catalog.py e as planilhas originais quando for atualizar os dados.
2. Execute node scripts/prepare_interno.mjs. O comando usa o modelo atualizado e os dados já embutidos, copiando somente a consulta e fotos WebP para .tmp/interno-assets/. As planilhas não são necessárias para atualizar a interface.
3. Execute node --test interno/src/worker.test.mjs.
4. Na primeira publicação, cadastre os três segredos no Worker pelo painel ou por wrangler secret bulk --config interno/wrangler.jsonc, fornecendo JSON por stdin. Não salve esse JSON em arquivos publicados.
5. Execute wrangler deploy --config interno/wrangler.jsonc. A configuração desativa workers.dev e URLs de prévia.
6. Confira que /, /expedicao.html e /fotos/NOME.webp redirecionam para /login sem sessão; que as duas senhas permitem consultar; e que Sair volta ao login. /expedicao.html continua indisponível mesmo com sessão: a consulta é servida apenas por /.

As pastas private/ e .tmp/ são ignoradas pelo Git. Não as publique no GitHub Pages nem em hospedagem estática sem o Worker de autenticação. Para atualizar os kits ou fotos, prepare e publique uma nova versão.
