import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import worker from './worker.mjs';

const origin = 'https://interno.rochaproauto.com.br';

function setup() {
  let reads = 0;
  let attempts = 0;
  const env = {
    ADMIN_PASSWORD: 'admin-example',
    STAFF_PASSWORD: 'staff-example',
    SESSION_SECRET: 'a-long-test-secret-with-more-than-thirty-two-characters',
    LOGIN_LIMITER: { async limit() { attempts++; return { success: attempts <= 5 }; } },
    PRIVATE_ASSETS: {
      async fetch(request) {
        reads++;
        const key = new URL(request.url).pathname;
        if (key === '/expedicao.html') return new Response('<html><head><title>Expedição local · RochaPro</title></head><body><header>ÁREA INTERNA · USO LOCAL</header><main><p class="local-note">Somente local.</p><img src="../assets/logo.svg"><img src="../private/fotos/kit-1.webp"></main><script>const KITS = [{"imagens":["private/fotos/kit-1.webp"]}];</script></body></html>');
        if (key === '/fotos/kit-1.webp') return new Response(new Uint8Array([1, 2, 3]));
        return new Response('Not found', { status: 404 });
      },
    },
  };
  return { env, reads: () => reads };
}

function request(path, options = {}) {
  return new Request(origin + path, options);
}

async function login(env, password) {
  return worker.fetch(request('/login', { method: 'POST', headers: { Origin: origin, 'CF-Connecting-IP': '192.0.2.1' }, body: new URLSearchParams({ password }) }), env);
}

test('private data and photos require a valid session', async () => {
  const state = setup();
  const page = await worker.fetch(request('/'), state.env);
  const photo = await worker.fetch(request('/fotos/kit-1.webp'), state.env);
  const rawPage = await worker.fetch(request('/expedicao.html'), state.env);
  assert.equal(page.status, 303);
  assert.equal(photo.status, 303);
  assert.equal(rawPage.status, 303);
  assert.equal(state.reads(), 0);
});

test('admin and staff passwords create separate roles without exposing credentials', async () => {
  for (const [password, role] of [['admin-example', 'Administrador'], ['staff-example', 'Equipe']]) {
    const state = setup();
    const response = await login(state.env, password);
    assert.equal(response.status, 303);
    const cookie = response.headers.get('Set-Cookie');
    assert.match(cookie, /HttpOnly; Secure; SameSite=Strict/);
    assert.doesNotMatch(cookie, /example/);
    const authenticated = await worker.fetch(request('/', { headers: { Cookie: cookie.split(';')[0] } }), state.env);
    assert.equal(authenticated.status, 200);
    const html = await authenticated.text();
    assert.match(html, new RegExp(`Sair · ${role}`));
    assert.match(html, /\/fotos\/kit-1.webp/);
    assert.match(html, /"imagens":\["fotos\/kit-1.webp"\]/);
    assert.doesNotMatch(html, /private\/fotos\//);
    assert.match(html, /https:\/\/rochaproauto.com.br\/assets\/logo.svg/);
    assert.doesNotMatch(html, /admin-example|staff-example/);
    assert.doesNotMatch(html, /USO LOCAL|local-note|Expedição local/);
    const photo = await worker.fetch(request('/fotos/kit-1.webp', { headers: { Cookie: cookie.split(';')[0] } }), state.env);
    assert.equal(photo.status, 200);
    assert.equal(photo.headers.get('Content-Type'), 'image/webp');
    assert.equal(photo.headers.get('Cache-Control'), 'private, no-store');
    const rawPage = await worker.fetch(request('/expedicao.html', { headers: { Cookie: cookie.split(';')[0] } }), state.env);
    assert.equal(rawPage.status, 404);
  }
});

test('deployment always runs authentication before serving assets', async () => {
  const config = JSON.parse(await readFile(new URL('../wrangler.jsonc', import.meta.url), 'utf8'));
  assert.equal(config.assets.run_worker_first, true);
  assert.equal(config.assets.html_handling, 'none');
  assert.equal(config.assets.not_found_handling, 'none');
  assert.equal(config.workers_dev, false);
  assert.equal(config.preview_urls, false);
});

test('wrong password, forged cookie and cross-origin login do not unlock data', async () => {
  const state = setup();
  assert.equal((await login(state.env, 'wrong')).status, 200);
  assert.equal((await worker.fetch(request('/', { headers: { Cookie: '__Host-rochapro_session=forged' } }), state.env)).status, 303);
  assert.equal((await worker.fetch(request('/login', { method: 'POST', headers: { Origin: 'https://other.example' }, body: new URLSearchParams({ password: 'admin-example' }) }), state.env)).status, 403);
  assert.equal(state.reads(), 0);
});

test('rate limit rejects further login attempts', async () => {
  const state = setup();
  for (let attempt = 0; attempt < 5; attempt++) await login(state.env, 'wrong');
  assert.equal((await login(state.env, 'admin-example')).status, 429);
});
