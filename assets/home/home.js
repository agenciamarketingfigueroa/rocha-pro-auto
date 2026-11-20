(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#main-menu');
  function closeMenu() { menuButton.setAttribute('aria-expanded','false'); menu.classList.remove('is-open'); }
  menuButton.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));menu.classList.toggle('is-open',open);});
  menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuButton.getAttribute('aria-expanded')==='true'){closeMenu();menuButton.focus();}});
  const search = document.querySelector('#model-search');
  const cards = [...document.querySelectorAll('[data-model]')];
  const filters = [...document.querySelectorAll('[data-category]')];
  const fold = s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  let category='Todos';
  function filterModels() {
    const query=fold(search.value);let found=0;
    for(const card of cards){const visible=(!query||fold(card.dataset.model).includes(query))&&(category==='Todos'||card.dataset.kind===category);card.hidden=!visible;if(visible)found++;}
    for(const group of document.querySelectorAll('.vehicle-grid'))group.hidden=![...group.children].some(card=>!card.hidden);
    document.querySelector('#model-count').textContent=`${found} ${found===1?'modelo para explorar':'modelos para explorar'}`;
    document.querySelector('#model-empty').hidden=found!==0;
    document.querySelector('#clear-models').hidden=!query&&category==='Todos';
  }
  filters.forEach(button=>button.addEventListener('click',()=>{category=button.dataset.category;filters.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filterModels();}));
  search.addEventListener('input',filterModels);
  document.querySelector('#clear-models').addEventListener('click',()=>{search.value='';category='Todos';filters.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.category==='Todos')));filterModels();search.focus();});
  document.querySelector('.model-controls').hidden=false;
})();
