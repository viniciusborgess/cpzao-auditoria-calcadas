// Service worker do app de auditoria de calçadas.
//
// Todos os caminhos são RELATIVOS ao escopo do service worker, nunca absolutos:
// o app é servido numa subpasta no GitHub Pages (/cpzao-auditoria-calcadas/),
// e caminhos começando com "/" apontariam para a raiz do domínio.
//
// Estratégia de cache:
//   • modelo .onnx e .wasm  -> cache-first (arquivos grandes e imutáveis)
//   • resto                 -> stale-while-revalidate (atualiza em segundo plano)
//
// Resultado: depois da primeira visita o app abre e infere sem rede — o que
// importa numa apresentação presencial, onde o Wi-Fi é imprevisível.

const CACHE = 'calcadas-v1';

const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache =>
      // addAll falha inteiro se um item falhar; aqui cada um é independente
      Promise.allSettled(SHELL.map(u => cache.add(u)))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // includes, não startsWith: sob subpasta o caminho é /<repo>/models/...
  if (url.pathname.includes('/models/') || url.pathname.endsWith('.wasm')) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  event.respondWith(staleWhileRevalidate(event.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const clone = response.clone();
    caches.open(CACHE).then(cache => cache.put(request, clone));
  }
  return response;
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  const fresh = await fetch(request).then(response => {
    if (response.ok) {
      const clone = response.clone();
      caches.open(CACHE).then(cache => cache.put(request, clone));
    }
    return response;
  }).catch(() => cached);
  return fresh || cached || new Response('Network error', { status: 500 });
}
