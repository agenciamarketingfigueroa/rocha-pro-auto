export const PURCHASE_PHONE = '5531971606904';
export const ORDER_LIMIT = 999999;
export const ORDER_UNITS = ['PC', 'PAR', 'KIT'];
export function supplierCode(value) { return String(value).trim().toUpperCase().replace(/\s+/g, ''); }
export function validCode(code) { return /^[A-Z0-9][A-Z0-9._-]*$/.test(code) && !/^0+$/.test(code) && !/^KIT\d+$/i.test(code); }
export function validQuantity(value) { return Number.isSafeInteger(value) && value > 0 && value <= ORDER_LIMIT; }
export function unitCode(value) {
  const unit = String(value || '').toUpperCase();
  return /^(PC|PCS|PÇ|PÇS|PEÇA|PEÇAS|UN|UND)$/.test(unit) ? 'PC' : unit === 'PARES' ? 'PAR' : unit;
}
export function compositionParts(value) { return String(value || '').split(/\s+\/\s+|\n+|\s*\|\s*/).map(p => p.trim().replace(/^\/\s*|\s*\/$/g, '')).filter(Boolean); }
export function parsePart(raw) {
  const external = /\b(PN\s*\d|PAUSE|JOÃO|JOAO|SOB\s+MEDIDA|ALFA)/i.test(raw);
  const match = raw.match(/^\s*(?:PAUSE\s*:?\s*)?([A-Z0-9][A-Z0-9._-]*(?:\s+\d+)?)\s*(?:\([^)]*\))?\s*:\s*(\d+)\s*(PC|PCS|PÇ|PÇS|PEÇA|PEÇAS|UN|UND|PAR|PARES|KIT)\s*(?:\([^)]*\))?\s*$/i);
  if (match) {
    const code = supplierCode(match[1]);
    return { code: validCode(code) ? code : '', quantity: validQuantity(Number(match[2])) ? Number(match[2]) : null, unit: unitCode(match[3]), raw, external };
  }
  const codeMatch = raw.match(/^\s*(?:PAUSE\s*:?\s*)?([A-Z0-9][A-Z0-9._-]*)\s*(?:\([^)]*\))?\s*:/i) || raw.match(/^\s*([A-Z0-9][A-Z0-9._-]*)\s*$/i);
  const code = codeMatch ? supplierCode(codeMatch[1]) : '';
  // Preserve uncertain annotations for manual review, without guessing amounts or units.
  return { code: validCode(code) ? code : '', quantity: null, unit: '', raw, external };
}
export function resolveKit(value, kits) {
  const input = supplierCode(value);
  const direct = kits.find(k => k.codigo.toUpperCase() === input);
  if (direct) return direct;
  const match = input.match(/^(?:KIT)?(\d{1,5})$/);
  if (!match) return null;
  const number = Number(match[1]);
  const code = `KIT${number >= 1 && number <= 9999 ? number + 10000 : number}`;
  return kits.find(k => k.codigo.toUpperCase() === code) || null;
}
export function findSupplier(value, kits) {
  const code = supplierCode(value);
  const matches = [];
  for (const kit of kits) for (const raw of compositionParts(kit.composicao)) {
    const part = parsePart(raw);
    if (part.code === code) matches.push({ ...part, kit: kit.codigo });
  }
  return matches;
}
export function validItem(item) { return validCode(item.code) && validQuantity(item.quantity) && ORDER_UNITS.includes(item.unit); }
export function addToOrder(order, parts, multiplier = 1) {
  if (!parts.length || !validQuantity(multiplier) || !parts.every(validItem)) throw new Error('Confira o código, a quantidade e a unidade de todas as peças.');
  const result = order.map(item => ({ ...item }));
  if (!result.every(validItem)) throw new Error('Corrija as quantidades do pedido antes de adicionar peças.');
  for (const part of parts) {
    const quantity = part.quantity * multiplier;
    const existing = result.find(item => item.code === part.code && item.unit === part.unit);
    const total = quantity + (existing?.quantity || 0);
    if (!validQuantity(total)) throw new Error('A quantidade máxima por código e unidade é 999999.');
    if (existing) existing.quantity = total;
    else result.push({ code: part.code, quantity, unit: part.unit });
  }
  return result;
}
export function purchaseMessage(order) {
  if (!order.length || !order.every(validItem)) return '';
  return ['Fala, Tigrinho! Tudo bem, meu amigo?', '', 'Preciso dessas peças da Borrachas Rocha:', '',
    ...order.map(item => `${item.quantity} ${item.unit} — código ${item.code}`),
    '', 'Consegue separar pra gente e me passar os valores? Valeu!'].join('\n');
}
export function purchaseUrl(order) { const message = purchaseMessage(order); return message ? `https://wa.me/${PURCHASE_PHONE}?text=${encodeURIComponent(message)}` : ''; }
