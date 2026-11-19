import { mkdir, readFile, readdir, copyFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = path.join(root, 'private');
const destination = path.join(root, '.tmp', 'interno-assets');
const old = await readFile(path.join(source, 'expedicao.html'), 'utf8');
const match = old.match(/const KITS = (.*);/);
if (!match) throw new Error('Arquivo interno sem dados de kits.');
const kits = JSON.parse(match[1]);
if (!Array.isArray(kits) || !kits.length) throw new Error('Nenhum kit disponível.');
const template = await readFile(path.join(root, 'expedicao', 'template.html'), 'utf8');
if (template.split('/*__KITS__*/ []').length !== 2) throw new Error('Modelo inválido.');
const html = template.replace('/*__KITS__*/ []', JSON.stringify(kits).replaceAll('<', '\\u003c'));
await mkdir(path.join(destination, 'fotos'), { recursive: true });
await mkdir(path.join(destination, 'brand'), { recursive: true });
const brand = path.join(root, 'assets', 'identidade-visual', '01-marca');
for (const filename of ['logo-horizontal-claro.svg', 'logo-horizontal-escuro.svg', 'favicon.svg', 'pwa-192.png', 'pwa-512.png']) {
  await copyFile(path.join(brand, filename), path.join(destination, 'brand', filename));
}
await copyFile(path.join(brand, 'apple-touch-icon-180.png'), path.join(destination, 'apple-touch-icon.png'));
await writeFile(path.join(destination, 'expedicao.html'), html);
const purchaseTemplate = await readFile(path.join(root, 'interno', 'pedido-compra.html'), 'utf8');
const purchaseCore = await readFile(path.join(root, 'interno', 'src', 'purchase-core.mjs'), 'utf8');
if (purchaseTemplate.split('/*__KITS__*/ []').length !== 2 || purchaseTemplate.split('/*__PURCHASE_CORE__*/').length !== 2) throw new Error('Modelo de pedido inválido.');
const purchaseHtml = purchaseTemplate.replace('/*__KITS__*/ []', JSON.stringify(kits).replaceAll('<', '\\u003c'))
  .replace('/*__PURCHASE_CORE__*/', purchaseCore.replace(/^export /gm, ''));
await writeFile(path.join(destination, 'pedido-compra.html'), purchaseHtml);
let photos = 0;
for (const entry of await readdir(path.join(source, 'fotos'), { withFileTypes: true })) {
  if (!entry.isFile() || !/^[a-z0-9][a-z0-9._-]*\.webp$/i.test(entry.name)) continue;
  await copyFile(path.join(source, 'fotos', entry.name), path.join(destination, 'fotos', entry.name));
  photos++;
}
console.log(`Publicação preparada: ${kits.length} kits e ${photos} fotos em .tmp/interno-assets.`);
