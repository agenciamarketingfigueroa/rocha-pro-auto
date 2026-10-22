(() => {
  const catalog = Array.isArray(window.ROCHAPRO_CATALOG) ? window.ROCHAPRO_CATALOG : [];
  const search = document.querySelector('#busca');
  const make = document.querySelector('#montadora');
  const job = document.querySelector('#funcao');
  const grid = document.querySelector('#products');
  const count = document.querySelector('#result-count');
  const note = document.querySelector('#result-note');
  const more = document.querySelector('#mais');
  const dialog = document.querySelector('#detail');
  if (location.protocol === 'file:' || ['localhost','127.0.0.1','[::1]'].includes(location.hostname)) {
    document.querySelector('#internal-link').hidden = false;
  }
  let shown = 24;
  const fold = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const params = new URLSearchParams(location.search);
  const allMakes = [...new Set(catalog.flatMap(item => item.montadoras))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  const requestedJobs = ['Amortecedor','Barra Estabilizadora Dianteira','Barra Estabilizadora Traseira','Cabine','Feixe de Mola','Bieleta','Batente','Calço anti ruído','Escapamento','Braço tensor','Carroceria','Bandeja','Tirante'];
  const allJobs = [...new Set([...requestedJobs, ...catalog.flatMap(item => item.funcoes)])].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  for (const value of allMakes) make.add(new Option(value,value));
  if(catalog.some(item=>!item.montadoras.length))make.add(new Option('Montadora não identificada','__nao_identificada__'));
  for (const value of allJobs) job.add(new Option(value,value));
  search.value = params.get('busca') || '';
  make.value = params.get('montadora') || '';
  job.value = params.get('funcao') || '';
  function el(tag, cls, content) { const n=document.createElement(tag); if(cls)n.className=cls; if(content!==undefined)n.textContent=content; return n; }
  function card(item){
    const root=el('article','card'), media=el('div','card-media');
    if(item.imagens.length){const image=el('img');image.src=item.imagens[0];image.alt=`Foto de ${item.nome}`;image.loading='lazy';media.append(image)}
    else media.append(el('div','no-photo','FOTO EM PREPARAÇÃO'));
    root.append(media);const body=el('div','card-body');body.append(el('span','code',item.codigo),el('h3','',item.nome),el('p','meta',`${item.funcoes.join(', ')} · ${item.montadoras.join(', ') || 'Montadora não identificada'}`));
    if(item.descricao)body.append(el('p','card-description',item.descricao));
    const actions=el('div','card-actions');
    const button=el('button','view','Ver detalhes →');button.type='button';button.addEventListener('click',()=>openDetail(item));actions.append(button);
    const add=el('button','add-cart','+ Adicionar');add.type='button';add.setAttribute('aria-label',`Adicionar ${item.codigo} ao carrinho`);add.addEventListener('click',()=>window.ROCHAPRO_CART.add(item.codigo));actions.append(add);
    body.append(actions);root.append(body);return root;
  }
  function openDetail(item){
    const content=document.querySelector('#detail-content');content.replaceChildren();content.append(el('p','code',item.codigo),el('h2','',item.nome),el('p','',`Funções: ${item.funcoes.join(', ')}`),el('p','',`Montadora: ${item.montadoras.join(', ') || 'Não identificada na descrição'}`));
    if(item.descricao){content.append(el('h3','','Descrição e aplicação'));content.append(el('div','detail-description',item.descricao))}
    if(item.imagens.length){const gallery=el('div','detail-gallery');for(const path of item.imagens){const image=el('img');image.src=path;image.alt=`Foto de ${item.nome}`;image.loading='lazy';gallery.append(image)}content.append(gallery)}
    else content.append(el('p','no-photo','FOTO EM PREPARAÇÃO'));
    content.append(el('p','detail-note','Confira aplicação, medidas e disponibilidade pelo seu canal comercial habitual antes da compra.'));
    const add=el('button','button detail-add','+ Adicionar ao carrinho');add.type='button';add.addEventListener('click',()=>window.ROCHAPRO_CART.add(item.codigo));content.append(add);dialog.showModal();
  }
  function render(){
    const query=fold(search.value.trim()), maker=make.value, role=job.value;
    const filtered=catalog.filter(item=>(!query||fold(`${item.codigo} ${item.nome} ${item.descricao}`).includes(query))&&(!maker||(maker==='__nao_identificada__'?!item.montadoras.length:item.montadoras.includes(maker)))&&(!role||item.funcoes.includes(role)));
    count.textContent=filtered.length.toLocaleString('pt-BR');note.textContent=`Exibindo ${Math.min(shown,filtered.length)} de ${filtered.length} produtos ativos.`;
    grid.replaceChildren(...filtered.slice(0,shown).map(card));
    if(!filtered.length)grid.append(el('div','empty','Nenhum produto encontrado. Tente outro termo ou limpe os filtros.'));
    more.hidden=shown>=filtered.length;
    const url=new URL(location.href);for(const [key,value] of [['busca',search.value.trim()],['montadora',maker],['funcao',role]])value?url.searchParams.set(key,value):url.searchParams.delete(key);
    history.replaceState(null,'',url.pathname+url.search+url.hash);
  }
  for(const input of [search,make,job])input.addEventListener(input===search?'input':'change',()=>{shown=24;render()});
  document.querySelector('#limpar').addEventListener('click',()=>{search.value='';make.value='';job.value='';shown=24;render();search.focus()});
  more.addEventListener('click',()=>{shown+=24;render()});
  document.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  render();
})();
