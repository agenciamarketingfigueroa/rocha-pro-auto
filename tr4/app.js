(() => {
  'use strict';
  const products = window.TR4_PRODUCTS || [];
  const selected = new Set();
  const activeCampaign = Date.now() < Date.parse('2026-12-01T03:00:00Z');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const wa = message => 'https://wa.me/5531973589165?text=' + encodeURIComponent(message);
  const greeting = activeCampaign ? 'Olá! Vim da campanha de fim de ano da Pajero TR4 e quero consultar as condições.' : 'Olá! Quero consultar os kits para minha Pajero TR4.';
  const cards = Array.from(document.querySelectorAll('.product-card'));
  const buttons = Array.from(document.querySelectorAll('[data-select]'));
  const search = document.querySelector('#product-search');
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  let category = 'all';
  if (!activeCampaign) {
    document.querySelectorAll('[data-campaign-text]').forEach(el => { el.textContent = el.dataset.campaignText; });
    document.querySelector('.hero-actions [data-contact]').textContent = 'Consultar valores';
    document.querySelector('.campaign-box [data-contact]').textContent = 'Consultar os kits';
  }
  document.querySelectorAll('[data-contact]').forEach(link => { link.href = wa(greeting); });
  try {
    const saved = JSON.parse(sessionStorage.getItem('rochapro-tr4-selection') || '[]');
    if (Array.isArray(saved)) saved.filter(code => products.some(p => p.codigo === code)).forEach(code => selected.add(code));
  } catch { /* Navegação privada continua funcionando sem persistência. */ }
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
    document.querySelector('#selected-help').textContent = count ? 'Sua lista está pronta para enviar à RochaPro.' : 'Selecione kits ou converse com a equipe.';
    document.querySelector('#clear-selection').hidden = !count;
    const link = document.querySelector('#quote-link');
    link.textContent = count ? `Cotar seleção (${count})` : 'Falar no WhatsApp';
    const list = products.filter(p => selected.has(p.codigo)).map(p => `• ${p.codigo} — ${p.nome}`).join('\n');
    link.href = wa(greeting + (count ? `\n\nTenho interesse nestes kits:\n${list}\n\nPodem me ajudar a confirmar a aplicação, os valores e a disponibilidade?` : ' Podem me ajudar a escolher os kits?'));
    try { sessionStorage.setItem('rochapro-tr4-selection', JSON.stringify([...selected])); } catch { /* Opcional. */ }
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
      const product = products.find(p => p.codigo === card.dataset.code);
      const visible = product && (category === 'all' || product.category === category) && normalize(product.codigo + ' ' + product.nome).includes(query);
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
