(() => {
  const PHONE = '5531973589165';
  const STORAGE_KEY = 'rochapro-carrinho-v1';
  const products = new Map((window.ROCHAPRO_CATALOG || []).map(item => [item.codigo, item]));
  const dialog = document.querySelector('#cart-dialog');
  const items = document.querySelector('#cart-items');
  const count = document.querySelector('#cart-count');
  const toggle = document.querySelector('#cart-toggle');
  const summary = document.querySelector('#cart-summary');
  const send = document.querySelector('#cart-whatsapp');
  const clear = document.querySelector('#cart-clear');
  const notice = document.querySelector('#cart-notice');
  let noticeTimer;

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      if (!saved || typeof saved !== 'object' || Array.isArray(saved)) return {};
      return Object.fromEntries(Object.entries(saved)
        .filter(([code, quantity]) => products.has(code) && Number.isInteger(quantity) && quantity >= 1 && quantity <= 999));
    } catch { return {}; }
  }
  let cart = load();

  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(cart)); }
    catch { flash('Não foi possível guardar o carrinho neste navegador.'); }
  }
  function flash(message) {
    notice.textContent = message;
    notice.hidden = false;
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { notice.hidden = true; }, 2600);
  }
  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }
  function setQuantity(code, quantity) {
    const next = Math.trunc(Number(quantity));
    if (!Number.isFinite(next) || next < 1) delete cart[code];
    else cart[code] = Math.min(next, 999);
    save();
    render();
  }
  function row(code, quantity) {
    const product = products.get(code);
    const line = element('article', 'cart-item');
    if (product.imagens.length) {
      const image = element('img', 'cart-thumb');
      image.src = product.imagens[0];
      image.alt = '';
      image.loading = 'lazy';
      line.append(image);
    } else line.append(element('div', 'cart-thumb placeholder', 'R'));
    const info = element('div');
    info.append(element('span', 'code', code), element('h3', '', product.nome));
    const bottom = element('div', 'cart-row');
    const controls = element('div', 'quantity-control');
    const minus = element('button', '', '−');
    minus.type = 'button'; minus.setAttribute('aria-label', `Diminuir quantidade de ${code}`);
    minus.addEventListener('click', () => setQuantity(code, quantity - 1));
    const input = element('input');
    input.type = 'number'; input.min = '1'; input.max = '999'; input.value = String(quantity);
    input.setAttribute('aria-label', `Quantidade de ${code}`);
    input.addEventListener('change', () => {
      const value = Number(input.value);
      if (!Number.isInteger(value) || value < 1 || value > 999) { input.value = String(cart[code]); return; }
      setQuantity(code, value);
    });
    const plus = element('button', '', '+');
    plus.type = 'button'; plus.setAttribute('aria-label', `Aumentar quantidade de ${code}`);
    plus.disabled = quantity >= 999;
    plus.addEventListener('click', () => setQuantity(code, quantity + 1));
    controls.append(minus, input, plus);
    const remove = element('button', 'cart-remove', 'Remover');
    remove.type = 'button'; remove.setAttribute('aria-label', `Remover ${code} do carrinho`);
    remove.addEventListener('click', () => setQuantity(code, 0));
    bottom.append(controls, remove);
    info.append(bottom); line.append(info);
    return line;
  }
  function message() {
    const lines = ['Olá! Gostaria de solicitar este pedido:', ''];
    for (const [code, quantity] of Object.entries(cart)) {
      const product = products.get(code);
      lines.push(`${quantity}x ${code} — ${product.nome}`);
    }
    lines.push('', 'Por favor, confirmem aplicação, disponibilidade e condições.');
    return lines.join('\n');
  }
  function render() {
    const entries = Object.entries(cart);
    const total = entries.reduce((sum, [, quantity]) => sum + quantity, 0);
    count.textContent = String(total);
    toggle.setAttribute('aria-label', `Abrir carrinho, ${total} ${total === 1 ? 'item' : 'itens'}`);
    items.replaceChildren();
    if (entries.length) items.append(...entries.map(([code, quantity]) => row(code, quantity)));
    else {
      const empty = element('p', 'cart-empty');
      empty.append(element('strong', '', 'Seu carrinho está vazio.'), 'Escolha uma peça no catálogo para começar.');
      items.append(empty);
    }
    summary.textContent = total ? `${total} ${total === 1 ? 'peça' : 'peças'} em ${entries.length} ${entries.length === 1 ? 'produto' : 'produtos'}` : 'Nenhum produto adicionado';
    clear.hidden = !entries.length;
    if (entries.length) {
      send.href = `https://wa.me/${PHONE}?text=${encodeURIComponent(message())}`;
      send.removeAttribute('aria-disabled');
    } else {
      send.removeAttribute('href');
      send.setAttribute('aria-disabled', 'true');
    }
  }
  window.ROCHAPRO_CART = {
    add(code) {
      if (!products.has(code)) return;
      if ((cart[code] || 0) >= 999) { flash('Quantidade máxima de 999 por produto.'); return; }
      cart[code] = (cart[code] || 0) + 1;
      save(); render(); flash(`${code} adicionado ao carrinho.`);
    }
  };
  toggle.addEventListener('click', () => dialog.showModal());
  document.querySelector('.cart-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  clear.addEventListener('click', () => {
    if (!Object.keys(cart).length || !confirm('Limpar todos os itens do carrinho?')) return;
    cart = {}; save(); render(); flash('Carrinho limpo.');
  });
  window.addEventListener('storage', event => { if (event.key === STORAGE_KEY) { cart = load(); render(); } });
  render();
})();
