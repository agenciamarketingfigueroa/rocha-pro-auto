const COOKIE = '__Host-rochapro_session';
const SESSION_SECONDS = 8 * 60 * 60;
const encoder = new TextEncoder();
const publicSite = 'https://rochaproauto.com.br';

function headers(contentType = 'text/html; charset=utf-8', nonce) {
  const policy = [
    "default-src 'none'",
    `script-src ${nonce ? `'nonce-${nonce}'` : "'none'"}`,
    "style-src 'unsafe-inline'",
    `img-src 'self' ${publicSite} data:`,
    "form-action 'self'",
    "base-uri 'none'",
    "frame-ancestors 'none'",
  ].join('; ');
  return {
    'Content-Type': contentType,
    'Cache-Control': 'private, no-store',
    'Content-Security-Policy': policy,
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'same-origin',
    'X-Frame-Options': 'DENY',
  };
}

function page(title, body, status = 200) {
  const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} · RochaPro</title><style>body{font:16px/1.5 system-ui,sans-serif;background:#f3f3f3;color:#171717;margin:0;padding:32px 16px}.box{max-width:380px;margin:10vh auto;background:#fff;border-radius:12px;padding:28px;box-shadow:0 5px 20px #0002}h1{font-size:1.5rem;margin:0 0 12px}label{display:block;font-weight:700;margin:20px 0 6px}input{font:inherit;width:100%;box-sizing:border-box;padding:12px;border:1px solid #888;border-radius:7px}button{font:700 1rem system-ui;background:#d00;color:#fff;border:0;border-radius:7px;padding:12px 18px;margin-top:18px;cursor:pointer}.error{color:#a00}a{color:#a00}</style></head><body><main class="box">${body}</main></body></html>`;
  return new Response(html, { status, headers: headers() });
}

function loginPage(error = false) {
  return page('Área interna', `<h1>Área interna</h1><p>Entre com a senha de administrador ou da equipe.</p>${error ? '<p class="error" role="alert">Senha inválida. Tente novamente.</p>' : ''}<form method="post" action="/login"><label for="password">Senha</label><input id="password" name="password" type="password" inputmode="numeric" autocomplete="current-password" required autofocus maxlength="128"><button type="submit">Entrar</button></form>`);
}

function base64url(bytes) {
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function unbase64url(value) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')), c => c.charCodeAt(0));
}

function equalBytes(left, right) {
  if (left.length !== right.length) return false;
  let difference = 0;
  for (let index = 0; index < left.length; index++) difference |= left[index] ^ right[index];
  return difference === 0;
}

async function digest(value) {
  return new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value)));
}

async function passwordRole(value, env) {
  const [entered, admin, staff] = await Promise.all([
    digest(value), digest(env.ADMIN_PASSWORD), digest(env.STAFF_PASSWORD),
  ]);
  const isAdmin = equalBytes(entered, admin);
  const isStaff = equalBytes(entered, staff);
  return isAdmin ? 'admin' : isStaff ? 'staff' : null;
}

async function signingKey(secret) {
  return crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}

async function createSession(role, secret) {
  const payload = base64url(encoder.encode(JSON.stringify({ role, expires: Date.now() + SESSION_SECONDS * 1000, nonce: base64url(crypto.getRandomValues(new Uint8Array(16))) })));
  const signature = base64url(new Uint8Array(await crypto.subtle.sign('HMAC', await signingKey(secret), encoder.encode(payload))));
  return `${payload}.${signature}`;
}

async function readSession(request, secret) {
  const raw = request.headers.get('Cookie')?.match(new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]+)`))?.[1];
  if (!raw || raw.length > 512) return null;
  const pieces = raw.split('.');
  if (pieces.length !== 2) return null;
  try {
    const signature = unbase64url(pieces[1]);
    const valid = await crypto.subtle.verify('HMAC', await signingKey(secret), signature, encoder.encode(pieces[0]));
    if (!valid) return null;
    const payload = JSON.parse(new TextDecoder().decode(unbase64url(pieces[0])));
    if (!['admin', 'staff'].includes(payload.role) || !Number.isSafeInteger(payload.expires) || payload.expires <= Date.now()) return null;
    return payload.role;
  } catch {
    return null;
  }
}

function redirect(path, cookie) {
  const response = new Response(null, { status: 303, headers: { ...headers(), Location: path } });
  if (cookie) response.headers.set('Set-Cookie', cookie);
  return response;
}

function sameOrigin(request) {
  const origin = request.headers.get('Origin');
  const site = request.headers.get('Sec-Fetch-Site');
  if (site && site !== 'same-origin') return false;
  // Pages opened before the policy fix can still submit Origin: null.
  // Accept these only when browser-controlled metadata proves same-origin.
  if (origin === 'null') return site === 'same-origin';
  return !origin || origin === new URL(request.url).origin;
}

async function privatePage(env) {
  const object = await env.PRIVATE_ASSETS.fetch(new Request('https://assets.internal/expedicao.html'));
  if (!object.ok) return page('Dados indisponíveis', '<h1>Dados ainda não enviados</h1><p>A consulta será liberada após importar a planilha de kits.</p>', 503);
  const nonce = base64url(crypto.getRandomValues(new Uint8Array(16)));
  const html = (await object.text())
    .replace('<title>Expedição local · RochaPro</title>', '<title>Área interna · RochaPro</title>')
    .replace('ÁREA INTERNA · USO LOCAL', 'ÁREA INTERNA')
    .replace(/<p class="local-note">[\s\S]*?<\/p>/, '')
    .replace('Arquivo local de uso interno.', 'Consulta interna protegida por senha.')
    .replaceAll('../private/fotos/', '/fotos/')
    .replaceAll('private/fotos/', 'fotos/')
    .replaceAll('../assets/', `${publicSite}/assets/`)
    .replaceAll('../index.html', `${publicSite}/`)
    .replace('<script>', `<script nonce="${nonce}">`);
  return new Response(html, { headers: headers('text/html; charset=utf-8', nonce) });
}

async function privatePhoto(env, path) {
  const match = path.match(/^\/fotos\/([a-z0-9][a-z0-9._-]*\.webp)$/i);
  if (!match) return new Response('Não encontrado', { status: 404, headers: headers('text/plain; charset=utf-8') });
  const object = await env.PRIVATE_ASSETS.fetch(new Request(`https://assets.internal/fotos/${match[1]}`));
  if (!object.ok) return new Response('Não encontrado', { status: 404, headers: headers('text/plain; charset=utf-8') });
  return new Response(object.body, { headers: headers('image/webp') });
}

export default {
  async fetch(request, env) {
    if (!env.ADMIN_PASSWORD || !env.STAFF_PASSWORD || env.ADMIN_PASSWORD === env.STAFF_PASSWORD || !env.SESSION_SECRET || env.SESSION_SECRET.length < 32 || !env.PRIVATE_ASSETS || !env.LOGIN_LIMITER) {
      return new Response('Configuração incompleta', { status: 503, headers: headers('text/plain; charset=utf-8') });
    }
    const url = new URL(request.url);
    if (url.pathname === '/login' && request.method === 'GET') return loginPage();
    if (url.pathname === '/login' && request.method === 'POST') {
      if (!sameOrigin(request)) return new Response('Origem inválida', { status: 403, headers: headers('text/plain; charset=utf-8') });
      const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
      const { success } = await env.LOGIN_LIMITER.limit({ key: ip });
      if (!success) return page('Aguarde', '<h1>Muitas tentativas</h1><p>Aguarde um minuto e tente novamente.</p>', 429);
      if (!request.headers.get('Content-Type')?.startsWith('application/x-www-form-urlencoded')) return loginPage(true);
      if (Number(request.headers.get('Content-Length')) > 1024) return loginPage(true);
      const body = await request.text();
      if (body.length > 1024) return loginPage(true);
      const password = new URLSearchParams(body).get('password') || '';
      if (!password || password.length > 128) return loginPage(true);
      const role = await passwordRole(password, env);
      if (!role) return loginPage(true);
      const token = await createSession(role, env.SESSION_SECRET);
      return redirect('/', `${COOKIE}=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${SESSION_SECONDS}`);
    }
    const role = await readSession(request, env.SESSION_SECRET);
    if (!role) return redirect('/login');
    if (url.pathname === '/logout' && request.method === 'POST') {
      if (!sameOrigin(request)) return new Response('Origem inválida', { status: 403, headers: headers('text/plain; charset=utf-8') });
      return redirect('/login', `${COOKIE}=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0`);
    }
    if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Método não permitido', { status: 405, headers: headers('text/plain; charset=utf-8') });
    if (url.pathname === '/' || url.pathname === '/index.html') return privatePage(env);
    if (url.pathname.startsWith('/fotos/')) return privatePhoto(env, url.pathname);
    return new Response('Não encontrado', { status: 404, headers: headers('text/plain; charset=utf-8') });
  },
};
