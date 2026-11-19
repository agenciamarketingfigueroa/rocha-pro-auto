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
await writeFile(path.join(destination, 'expedicao.html'), html);
let photos = 0;
for (const entry of await readdir(path.join(source, 'fotos'), { withFileTypes: true })) {
  if (!entry.isFile() || !/^[a-z0-9][a-z0-9._-]*\.webp$/i.test(entry.name)) continue;
  await copyFile(path.join(source, 'fotos', entry.name), path.join(destination, 'fotos', entry.name));
  photos++;
}
console.log(`Publicação preparada: ${kits.length} kits e ${photos} fotos em .tmp/interno-assets.`);
