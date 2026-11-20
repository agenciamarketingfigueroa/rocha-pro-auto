export const models = [
  {
    slug: 'troller', name: 'Troller', fullName: 'Troller T4', match: /\btroller\b/i,
    hero: '/assets/site/troller-hero.webp', featured: 'KIT10363',
    headline: 'SEU TROLLER.<br>O PRÓXIMO<br><em>CAMINHO.</em>',
    description: 'Kits de buchas para Troller: barra estabilizadora, barra Panhard, braços tensores e amortecedor. Encontre a aplicação e cote com a RochaPro.',
    intro: 'Da revisão antes da trilha ao cuidado na volta. Encontre os kits do seu Troller e organize a manutenção com quem conhece o caminho.',
    planning: 'A TRILHA COMEÇA<br>COM A <span>REVISÃO.</span>',
    lead: 'Ter um destino é bom. Preparar o carro para ele é melhor.',
    text: 'Antes de escolher peças, identifique o ano, a versão e o conjunto que precisa de manutenção. Há aplicações específicas de 2002 a 2014 e itens cuja faixa de anos precisa ser confirmada.',
    featureTitle: 'UM PONTO DA<br>REVISÃO QUE<br><span>MERECE ATENÇÃO.</span>',
    featureText: 'O KIT10363 aparece no cadastro para a barra estabilizadora traseira do Troller de 2002 a 2014. Confira a aplicação com a equipe antes de pedir.',
    fitmentNote: 'As aplicações de 2002 a 2014 não devem ser estendidas automaticamente ao T4 de geração posterior.',
    article: 'troller-revisao-antes-e-depois-da-trilha',
  },
  {
    slug: 'hilux', name: 'Hilux', fullName: 'Toyota Hilux', match: /\bhilux\b/i,
    // SW4-only records are not pickup applications. Explicit Hilux / SW4 records remain.
    accepts: p => !/sw4/i.test(p.nome) || /hilux\s*\/\s*sw4/i.test(p.nome),
    hero: '/assets/site/hilux-hero.webp', featured: 'KIT10124',
    headline: 'SUA HILUX.<br>PRONTA PARA<br><em>CONTINUAR.</em>',
    description: 'Kits de buchas para Toyota Hilux: feixe de mola, amortecedor, estabilizadora e cabine. Consulte anos, medidas e aplicação com a RochaPro.',
    intro: 'No trabalho, na estrada ou nos planos do fim de semana. Organize a revisão da sua Hilux com os kits e as medidas certos.',
    planning: 'QUEM RODA MUITO<br>PRECISA DE <span>CUIDADO.</span>',
    lead: 'A rotina muda. A atenção aos detalhes continua.',
    text: 'Ano, versão, posição da peça e medidas fazem parte da escolha. Uma bucha de 35 mm não deve ser substituída por outra só porque o nome do veículo é o mesmo.',
    featureTitle: 'DO CADASTRO<br>PARA A SUA<br><span>REVISÃO.</span>',
    featureText: 'O KIT10124 é cadastrado para o feixe de mola traseiro da Hilux. Como o título não informa uma faixa de anos, a aplicação deve ser confirmada antes da compra.',
    fitmentNote: 'Esta seleção é da Hilux picape. Itens exclusivos da SW4 ficam fora; aplicações compartilhadas só aparecem quando o cadastro informa Hilux / SW4.',
    article: 'hilux-buchas-medidas-e-aplicacao',
  },
  {
    slug: 'frontier', name: 'Frontier', fullName: 'Nissan Frontier', match: /\bfrontier\b/i,
    hero: '/assets/site/frontier-hero.webp', featured: 'KIT10242',
    headline: 'SUA FRONTIER.<br>MAIS PLANOS.<br><em>MAIS CUIDADO.</em>',
    description: 'Kits para Nissan Frontier: buchas, jumelo, amortecedor, estabilizadora e anti-ruído. Encontre os códigos e confirme a geração com a RochaPro.',
    intro: 'Cada geração tem seus detalhes. Encontre os kits da sua Frontier, confira a aplicação e prepare a próxima manutenção.',
    planning: 'A MESMA FRONTIER?<br>CONFIRA A <span>GERAÇÃO.</span>',
    lead: 'O nome do carro é o começo da busca.',
    text: 'Os conjuntos de suspensão e as medidas variam entre versões. Informe ano, modelo e posição da peça para conferir a compatibilidade antes de fechar sua cotação.',
    featureTitle: 'CUIDADO COM<br>O CONJUNTO.<br><span>ATENÇÃO AO ANO.</span>',
    featureText: 'O KIT10242 reúne buchas da mola e do jumelo traseiro, com aplicação cadastrada para Frontier até 2012. Essa indicação não deve ser estendida às gerações seguintes.',
    fitmentNote: 'Existem diferenças de suspensão entre gerações. Expressões como “em diante” no cadastro não dispensam a confirmação da versão e do conjunto instalado.',
    article: 'frontier-geracoes-suspensao-e-buchas',
  },
];

export const vehicleLinks = [
  {slug:'tr4', name:'Pajero TR4', hero:'/tr4/assets/tr4-hero.webp'},
  ...models.map(({slug,name,hero}) => ({slug,name,hero})),
];

export function selectProducts(model, catalog) {
  return catalog.filter(p => model.match.test(p.nome) && (!model.accepts || model.accepts(p)))
    .sort((a,b) => Number(b.codigo === model.featured) - Number(a.codigo === model.featured) || Number(Boolean(b.imagens.length)) - Number(Boolean(a.imagens.length)) || a.codigo.localeCompare(b.codigo));
}

export const categoryLabels = {estabilizadora:'Estabilizadora e bieleta', bracos:'Braços e Panhard', molas:'Molas e jumelo', amortecedor:'Amortecedor', cabine:'Cabine', outros:'Outros kits'};
export function categoryFor(name) {
  return /estabilizadora|bieleta/i.test(name) ? 'estabilizadora' : /braço|tensor|panhard/i.test(name) ? 'bracos' : /mola|jumelo/i.test(name) ? 'molas' : /amortecedor/i.test(name) ? 'amortecedor' : /cabine/i.test(name) ? 'cabine' : 'outros';
}
