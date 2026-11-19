# Área interna online

O catálogo público continua no GitHub Pages. `interno.rochaproauto.com.br` será servido por um Cloudflare Worker separado. A consulta de kits usa o HTML gerado em `private/expedicao.html`, guardado em um bucket R2 privado; o Worker só o entrega depois do login. As fotos privadas passam pelo mesmo controle de acesso.

O Worker distingue os papéis `admin` e `staff`. Nesta versão, os dois papéis podem consultar as mesmas fichas; o papel de administrador fica disponível para futuras funções exclusivas. As senhas escolhidas pela loja devem ser cadastradas como **segredos** `ADMIN_PASSWORD` e `STAFF_PASSWORD` no painel da Cloudflare, nunca neste repositório nem em arquivos publicados. Também é preciso cadastrar `SESSION_SECRET` com um valor aleatório de pelo menos 32 caracteres. As sessões duram oito horas e podem ser encerradas pelo botão **Sair**. O formulário de login limita as tentativas por IP a cinco por minuto.

## Para ativar quando as planilhas estiverem no outro computador

1. Gere `private/expedicao.html` e `private/fotos/` com `python3 scripts/build_catalog.py PRODUTOS.xls KITS.xls`, usando os caminhos reais das planilhas. Não faça commit nem envie a pasta `private/` ao GitHub Pages.
2. Na conta Cloudflare do domínio, crie um bucket R2 chamado `rochapro-interno`. Mantenha o acesso público do bucket desativado.
3. Crie um Worker chamado `rochapro-interno` e cadastre os três segredos em **Workers & Pages → Worker → Settings → Variables and Secrets**. Informe as senhas escolhidas pela loja nos respectivos campos; gere `SESSION_SECRET` com um gerador de valores aleatórios. Não use as senhas como variáveis comuns em `wrangler.jsonc`.
4. No diretório `interno/`, execute `npx wrangler deploy`. A configuração cria o domínio personalizado `interno.rochaproauto.com.br`, desativa `workers.dev` e URLs de prévia, vincula o bucket privado e aplica o limite de tentativas. O domínio precisa estar ativo na Cloudflare.
5. Envie `private/expedicao.html` ao objeto `expedicao.html` do bucket e cada arquivo de `private/fotos/` ao prefixo `fotos/`. Exemplo para o HTML, a partir da raiz do repositório: `npx wrangler r2 object put rochapro-interno/expedicao.html --file private/expedicao.html --remote --config interno/wrangler.jsonc`. Para as fotos, use a mesma operação com o destino `rochapro-interno/fotos/NOME.webp`.
6. Teste que `/` e `/fotos/NOME.webp` redirecionam para `/login` sem sessão, que ambas as senhas permitem consultar, que uma senha errada não permite consultar e que **Sair** encerra o acesso. Só depois adicione um link no catálogo público.

As senhas numéricas escolhidas são curtas para um serviço exposto à internet. O limite de tentativas reduz ataques simples, mas pode ser contornado por origens distribuídas. Antes da ativação pública, recomendamos também uma política Cloudflare Access para restringir quem chega ao Worker, ou senhas mais longas. Se usar Access no Worker, proteja **todo o tráfego**, incluindo produção e prévias.
