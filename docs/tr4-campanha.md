# Página de vendas Pajero TR4

URL: https://rochaproauto.com.br/tr4/

Campanha confirmada pelo responsável: todos os kits da TR4 até 30/11/2026. Não foi informado percentual, preço ou condição de pagamento; a página encaminha a consulta para o WhatsApp comercial 55 31 97358-9165. Não usa o contato do representante de compras da área interna.

## Conteúdo e atualização

Os 13 kits vêm exclusivamente de `data/catalogo-publico.js`. A geração não lê a composição privada nem códigos de fornecedores. Quatro kits têm fotografias reais disponíveis: KIT10055, KIT10082, KIT10170 e KIT10273. Os outros nove exibem “Foto sob consulta”. As aplicações sem anos no nome não recebem uma faixa de anos presumida.

Editar `tr4/page.template.html`, `tr4/style.css` e `tr4/app.js`. Após atualizar o catálogo, executar:

```sh
node scripts/build_tr4.mjs
node scripts/test_tr4.mjs
```

O JavaScript substitui as chamadas da campanha por conteúdo permanente a partir de 01/12/2026, 00h de Brasília. O HTML e os metadados da campanha devem ser atualizados em uma futura campanha. A seleção fica no armazenamento da sessão do navegador e pode ser limpa; o WhatsApp só abre ao clicar, sem envio automático.

## Identidade e imagens

Direção visual baseada no sistema editorial e nas peças existentes de `rochapro-social`: Montserrat, preto, vermelho, prata, fotografia industrial e destaque para produtos reais. Marca original em `assets/identidade-visual/01-marca`. Montserrat local com licença OFL em `tr4/assets/OFL.txt` (fonte: repositório oficial google/fonts, diretório ofl/montserrat).

As duas cenas do automóvel foram criadas com a ferramenta integrada `image_gen.imagegen`; são identificadas como imagens ilustrativas. As fotografias dos kits não foram geradas nem alteradas. Os PNG originais foram preservados na pasta de imagens geradas e convertidos para WebP no projeto:

- `tr4/assets/tr4-hero.webp` — 1672 × 941, prata, estúdio preto com luz vermelha, veículo à direita.
- `tr4/assets/tr4-road.webp` — 1774 × 887, veículo estacionado junto a uma estrada de montanha, cena complementar.

### Prompt da hero

Use case: ads-marketing. Asset type: premium automotive website hero photograph, wide landscape 1536x1024 or wider. Create a photorealistic silver Mitsubishi Pajero TR4, Brazilian 2010-2015 facelift compact five-door SUV, recognizable short upright compact body, tall cabin, roof rails, rear spare tire, original stock wheels, distinctive rounded rectangular headlights and Mitsubishi grille. NOT a pickup, NOT Pajero Sport, NOT full-size Pajero. Parked on dark industrial concrete in a black studio with subtle red rim lighting and soft neutral overhead light, restrained haze and real reflections. Three-quarter front angle, all vehicle and wheels visible, vehicle occupies the RIGHT 65 percent, facing slightly left. Left 30 percent dark negative space for HTML copy, and empty dark upper area. Elegant rugged automotive campaign for RochaPro Auto Peças, palette black charcoal silver with controlled red accent. No people, no added parts, no written text, no prices, no typography, no watermark. Image is illustrative campaign artwork, not technical fitment evidence.

### Prompt da cena complementar

Use case: lighting-weather and compositing. Asset type: wide photographic banner for the same RochaPro Pajero TR4 campaign. Use the referenced image as the vehicle identity reference. Keep the recognizable silver Mitsubishi Pajero TR4 compact five-door SUV, stock body, headlights, wheels and proportions. Create a different complementary scene: this same vehicle parked safely beside a quiet scenic Brazilian mountain road at late afternoon, three-quarter rear/side view, spare wheel visible, no people and no motion. Car positioned on LEFT half of a wide panoramic frame, dark mountainous landscape stretching to the right with usable negative space for website copy. Natural charcoal, stone and warm muted sunlight, cinematic but credible, premium editorial automotive photography. No red studio lighting here. No words, lettering, graphic overlays, watermarks, captions or invented parts. Entire car in frame. This is illustrative campaign artwork.

## Validação

Cobertura integral do catálogo TR4, referências locais, busca com e sem acento, filtros por aplicação, cotação múltipla, remoção individual, limpeza, restauração da sessão e expiração no horário de Brasília verificadas por `scripts/test_tr4.mjs`. A ferramenta de navegador estava indisponível durante esta entrega; não foi possível validar visualmente a renderização final no desktop e no iPhone.
