(() => {
  'use strict';
  const { slug, name, products } = window.ROCHAPRO_MODEL;
  const selected = new Set();
  const key = `rochapro-${slug}-selection`;
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const wa = message => 'https://wa.me/5531973589165?text=' + encodeURIComponent(message);
  const greeting = `Olá! Quero consultar os kits para ${name}.`;
  const cards = Array.from(document.querySelectorAll('.product-card'));
  const buttons = Array.from(document.querySelectorAll('[data-select]'));
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  const search = document.querySelector('#product-search');
  let category = 'all';
  document.querySelectorAll('[data-contact]').forEach(link => { link.href = wa(greeting); });
  try {
    const saved = JSON.parse(sessionStorage.getItem(key) || '[]');
    if (Array.isArray(saved)) saved.filter(code => products.some(p => p.codigo === code)).forEach(code => selected.add(code));
  } catch { /* Persistence is optional. */ }
  function refreshSelection() {
    buttons.forEach(button => {
      const chosen = selected.has(button.dataset.select);
      button.setAttribute('aria-pressed', String(chosen));
      button.setAttribute('aria-label', `${chosen ? 'Remover' : 'Adicionar'} ${button.dataset.select} ${chosen ? 'da' : 'à'} cotação`);
      button.textContent = chosen ? 'Adicionado · remover' : 'Adicionar à cotação';
    });
    cards.forEach(card => card.classList.toggle('selected', selected.has(card.dataset.code)));
    const count = selected.size;
    document.querySelector('#selected-count').textContent = count ? `${count} ${count === 1 ? 'kit selecionado' : 'kits selecionados'}` : 'Monte sua cotação';
    document.querySelector('#selected-help').textContent = count ? 'Confirme a aplicação com nossa equipe.' : 'Selecione os kits que deseja consultar.';
    document.querySelector('#clear-selection').hidden = !count;
    const link = document.querySelector('#quote-link');
    link.textContent = count ? `Cotar seleção (${count})` : 'Falar no WhatsApp';
    const list = products.filter(p => selected.has(p.codigo)).map(p => `• ${p.codigo} — ${p.nome}`).join('\n');
    link.href = wa(greeting + (count ? `\n\nTenho interesse nestes kits:\n${list}\n\nPodem confirmar aplicação, valores e disponibilidade?` : ' Podem me ajudar a escolher?'));
    try { sessionStorage.setItem(key, JSON.stringify([...selected])); } catch { /* Optional. */ }
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    const code = button.dataset.select;
    selected.has(code) ? selected.delete(code) : selected.add(code);
    refreshSelection();
    document.querySelector('#selection-status').textContent = `${code} ${selected.has(code) ? 'adicionado à' : 'removido da'} cotação.`;
  }));
  document.querySelector('#clear-selection').addEventListener('click', () => {
    selected.clear(); refreshSelection();
    document.querySelector('#selection-status').textContent = 'Seleção limpa.';
    document.querySelector('#quote-link').focus();
  });
  function filterProducts() {
    const query = normalize(search.value.trim());
    let count = 0;
    cards.forEach(card => {
      const p = products.find(p => p.codigo === card.dataset.code);
      const visible = p && (category === 'all' || p.category === category) && normalize(p.codigo + ' ' + p.nome).includes(query);
      card.hidden = !visible;
      if (visible) count++;
    });
    document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'kit encontrado' : 'kits encontrados'}`;
    document.querySelector('#no-results').hidden = count !== 0;
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(filter => { filter.classList.toggle('active', filter === button); filter.setAttribute('aria-pressed', String(filter === button)); });
    filterProducts();
  }));
  search.addEventListener('input', filterProducts);
  refreshSelection();
})();
