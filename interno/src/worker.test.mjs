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
        if (key === '/pedido-compra.html') return new Response('<html><head><title>Pedido de compra · RochaPro</title></head><body><header><h1>Pedido de compra</h1></header><main>Pedido para Tigrinho</main><script>const KITS = [];</script></body></html>');
        if (key === '/expedicao.html') return new Response('<html><head><title>Expedição local · RochaPro</title></head><body><header>ÁREA INTERNA · USO LOCAL</header><main><p class="local-note">Somente local.</p><img src="../assets/identidade-visual/01-marca/logo-horizontal-claro.svg"><img src="../private/fotos/kit-1.webp"></main><script>const KITS = [{"imagens":["private/fotos/kit-1.webp"]}];</script></body></html>');
        if (key === '/fotos/kit-1.webp') return new Response(new Uint8Array([1, 2, 3]));
        if (key.startsWith('/brand/') || key === '/apple-touch-icon.png') return new Response('brand-fixture');
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

test('purchase tool uses the same authentication and has navigation to Consulta', async () => {
  for (const password of ['admin-example','staff-example']) {
    const state=setup();
    assert.equal((await worker.fetch(request('/pedido-de-compra'),state.env)).status,303);
    const session=await login(state.env,password);
    const options={headers:{Cookie:session.headers.get('Set-Cookie').split(';')[0]}};
    const purchase=await worker.fetch(request('/pedido-de-compra',options),state.env);
    assert.equal(purchase.status,200);
    const html=await purchase.text();
    assert.match(html,/Pedido para Tigrinho/);
    assert.match(html,/href="\/consulta"/);
    assert.match(html,/href="\/pedido-de-compra" aria-current="page"/);
    assert.match(html,/<script nonce="/);
    const consulta=await worker.fetch(request('/consulta',options),state.env);
    assert.equal(consulta.status,200);
    assert.match(await consulta.text(),/href="\/consulta" aria-current="page"/);
    assert.equal((await worker.fetch(request('/pedido-compra.html',options),state.env)).status,404);
  }
});

test('admin and staff passwords create separate roles without exposing credentials', async () => {
  for (const [password, role] of [['admin-example', 'admin'], ['staff-example', 'staff']]) {
    const state = setup();
    const response = await login(state.env, password);
    assert.equal(response.status, 303);
    const cookie = response.headers.get('Set-Cookie');
    assert.match(cookie, /HttpOnly; Secure; SameSite=Strict/);
    assert.doesNotMatch(cookie, /example/);
    assert.equal(JSON.parse(Buffer.from(cookie.split('=')[1].split('.')[0], 'base64url')).role, role);
    const authenticated = await worker.fetch(request('/', { headers: { Cookie: cookie.split(';')[0] } }), state.env);
    assert.equal(authenticated.status, 200);
    const html = await authenticated.text();
    assert.doesNotMatch(html, /Sair ·|action="\/logout"/);
    assert.match(html, /\/fotos\/kit-1.webp/);
    assert.match(html, /"imagens":\["fotos\/kit-1.webp"\]/);
    assert.doesNotMatch(html, /private\/fotos\//);
    assert.match(html, /src="\/brand\/logo-horizontal-claro.svg"/);
    assert.match(html, /rel="apple-touch-icon" sizes="180x180" href="\/apple-touch-icon.png"/);
    assert.match(html, /rel="manifest" href="\/manifest.webmanifest"/);
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

test('iPhone icons, manifest and logos are available before login while kit files remain private', async () => {
  const state = setup();
  for (const [path, type] of [
    ['/apple-touch-icon.png', 'image/png'],
    ['/brand/pwa-192.png', 'image/png'],
    ['/brand/pwa-512.png', 'image/png'],
    ['/brand/favicon.svg', 'image/svg+xml'],
    ['/brand/logo-horizontal-claro.svg', 'image/svg+xml'],
    ['/brand/logo-horizontal-escuro.svg', 'image/svg+xml'],
  ]) {
    const response = await worker.fetch(request(path), state.env);
    assert.equal(response.status, 200, path);
    assert.equal(response.headers.get('Content-Type'), type);
    assert.equal(response.headers.get('Set-Cookie'), null);
  }
  const manifestResponse = await worker.fetch(request('/manifest.webmanifest'), state.env);
  assert.equal(manifestResponse.status, 200);
  const manifest = await manifestResponse.json();
  assert.equal(manifest.start_url, '/');
  assert.equal(manifest.display, 'standalone');
  assert.equal(manifest.short_name, 'RochaPro');
  const loginPage = await worker.fetch(request('/login'), state.env);
  assert.match(loginPage.headers.get('Content-Security-Policy'), /manifest-src 'self'/);
  const html = await loginPage.text();
  assert.match(html, /src="\/brand\/logo-horizontal-escuro.svg"/);
  assert.match(html, /rel="apple-touch-icon" sizes="180x180" href="\/apple-touch-icon.png"/);
  for (const path of ['/fotos/kit-1.webp', '/expedicao.html', '/brand/private.webp']) {
    const response = await worker.fetch(request(path), state.env);
    assert.equal(response.status, 303);
    assert.equal(response.headers.get('Location'), '/login');
  }
  const head = await worker.fetch(request('/apple-touch-icon.png', { method: 'HEAD' }), state.env);
  assert.equal(head.status, 200);
  assert.equal(await head.text(), '');
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

test('browser form posts with a suppressed Origin can log in and out on the same origin', async () => {
  const state = setup();
  const browserHeaders = { Origin: 'null', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document' };
  const response = await worker.fetch(request('/login', {
    method: 'POST', headers: browserHeaders, body: new URLSearchParams({ password: 'admin-example' }),
  }), state.env);
  assert.equal(response.status, 303);
  const cookie = response.headers.get('Set-Cookie').split(';')[0];
  const logout = await worker.fetch(request('/logout', {
    method: 'POST', headers: { ...browserHeaders, Cookie: cookie },
  }), state.env);
  assert.equal(logout.status, 303);
  assert.match(logout.headers.get('Set-Cookie'), /Max-Age=0/);
});

test('login page preserves the origin for same-origin browser form submissions', async () => {
  const response = await worker.fetch(request('/login'), setup().env);
  assert.equal(response.headers.get('Referrer-Policy'), 'same-origin');
});

test('null and missing origins do not allow cross-site or sibling-domain form submissions', async () => {
  for (const headers of [
    { Origin: 'null' },
    { Origin: 'null', 'Sec-Fetch-Site': 'cross-site' },
    { Origin: 'null', 'Sec-Fetch-Site': 'same-site' },
    { 'Sec-Fetch-Site': 'cross-site' },
    { Origin: 'https://other.example', 'Sec-Fetch-Site': 'same-origin' },
  ]) {
    const state = setup();
    const response = await worker.fetch(request('/login', {
      method: 'POST', headers, body: new URLSearchParams({ password: 'admin-example' }),
    }), state.env);
    assert.equal(response.status, 403, JSON.stringify(headers));
    assert.equal(response.headers.get('Set-Cookie'), null);
    const session = await login(state.env, 'admin-example');
    const logout = await worker.fetch(request('/logout', {
      method: 'POST', headers: { ...headers, Cookie: session.headers.get('Set-Cookie').split(';')[0] },
    }), state.env);
    assert.equal(logout.status, 403);
    assert.equal(logout.headers.get('Set-Cookie'), null);
  }
});
