// Cloudflare Pages Function: POST /api/contact
// Validates a website inquiry and relays it to the DNNR Telegram inquiries group.
//
// Secrets (Pages project → Settings → Variables, or `wrangler pages secret put`):
//   TELEGRAM_BOT_TOKEN  – @dnnr_user_feedback_bot token
//   TELEGRAM_CHAT_ID    – chat id of the "DNNR Website Inquiries" group
//
// Cost: only /api/* invokes Functions (see /_routes.json); static pages stay free.
// Abuse guards: honeypot, minimum fill time, per-IP rate limit (Cache API, per colo),
// field length caps, email syntax + DNS (MX/A) check.

const ALLOWED_ORIGINS = new Set(['https://dnnr.us', 'https://www.dnnr.us', 'https://dnnr.mrsap.com']);
const TOPICS = new Set(['Consulting inquiry', 'Partnership', 'App support', 'Privacy request', 'Data deletion request', 'Other']);
const RATE_LIMIT = { max: 5, windowSec: 600 };
const LIMITS = { name: 100, email: 200, company: 120, message: 4000, button: 80, page: 200, source: 60, host: 60 };

// Human-readable names for data-source ids set on buttons/forms.
const SOURCE_LABELS = {
  nav_contact: 'Header · Contact',
  home_hero: 'Home · hero',
  home_services: 'Home · consulting services',
  home_cta: 'Home · bottom CTA',
  services_hero: 'Services · hero',
  services_row: 'Services · service card',
  services_form: 'Services · inline form',
  apps_cta: 'Apps · bottom CTA',
  support_contact: 'Support · contact',
  support_deletion: 'Support · data deletion',
  delete_page: 'Data deletion page',
  privacy_page: 'Privacy policy',
  contact_page: 'Contact page',
  footer_contact: 'Footer · Contact',
};

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowed = ALLOWED_ORIGINS.has(origin) || /^https:\/\/[a-z0-9-]+\.dnnr-us-official-website\.pages\.dev$/.test(origin);
  return allowed
    ? { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Vary': 'Origin' }
    : { 'Vary': 'Origin' };
}

function json(request, status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...corsHeaders(request) },
  });
}

const clean = (v, max) => String(v ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim().slice(0, max);
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$/;

async function domainAcceptsMail(domain) {
  // DNS-over-HTTPS; if the resolver is unreachable, don't block the user.
  const q = async (type) => {
    const r = await fetch(`https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(domain)}&type=${type}`, { headers: { accept: 'application/dns-json' } });
    if (!r.ok) throw new Error('doh');
    return r.json();
  };
  try {
    const mx = await q('MX');
    if (mx.Status === 3) return false; // NXDOMAIN
    if (Array.isArray(mx.Answer) && mx.Answer.length) return true;
    const a = await q('A');
    return Array.isArray(a.Answer) && a.Answer.length > 0;
  } catch {
    return true;
  }
}

async function rateLimited(ip) {
  const cache = caches.default;
  const key = new Request(`https://rate-limit.internal/contact/${encodeURIComponent(ip)}`);
  const hit = await cache.match(key);
  const count = hit ? Number(await hit.text()) || 0 : 0;
  if (count >= RATE_LIMIT.max) return true;
  await cache.put(key, new Response(String(count + 1), { headers: { 'Cache-Control': `max-age=${RATE_LIMIT.windowSec}` } }));
  return false;
}

export async function onRequestOptions({ request }) {
  return new Response(null, { status: 204, headers: corsHeaders(request) });
}

export async function onRequestPost({ request, env }) {
  if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) {
    return json(request, 503, { ok: false, error: 'Contact is temporarily unavailable. Please email hello@dnnr.us.' });
  }

  let data;
  try {
    const ct = request.headers.get('Content-Type') || '';
    data = ct.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch {
    return json(request, 400, { ok: false, error: 'Invalid request.' });
  }

  // Bots: honeypot filled or submitted implausibly fast → pretend success, drop silently.
  if (clean(data.website, 200) || Number(data.elapsed_ms) < 2500) {
    return json(request, 200, { ok: true });
  }

  const f = {
    name: clean(data.name, LIMITS.name),
    email: clean(data.email, LIMITS.email).toLowerCase(),
    company: clean(data.company, LIMITS.company),
    topic: TOPICS.has(data.topic) ? data.topic : 'Other',
    message: clean(data.message, LIMITS.message),
    source: clean(data.source, LIMITS.source).replace(/[^a-z0-9_-]/gi, '') || 'unknown',
    button: clean(data.button, LIMITS.button),
    page: clean(data.page, LIMITS.page),
    host: clean(data.host, LIMITS.host),
  };

  if (!f.name) return json(request, 422, { ok: false, field: 'name', error: 'Please enter your name.' });
  if (!EMAIL_RE.test(f.email)) return json(request, 422, { ok: false, field: 'email', error: 'Please enter a valid email so we can reply.' });
  if (f.message.length < 10) return json(request, 422, { ok: false, field: 'message', error: 'Please tell us a little more (10+ characters).' });
  if (!(await domainAcceptsMail(f.email.split('@')[1]))) {
    return json(request, 422, { ok: false, field: 'email', error: "That email domain doesn't seem to receive mail. Please check it." });
  }

  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (await rateLimited(ip)) {
    return json(request, 429, { ok: false, error: 'Too many messages. Please try again later or email hello@dnnr.us.' });
  }

  const cf = request.cf || {};
  const now = new Date();
  const pt = now.toLocaleString('en-US', { timeZone: 'America/Los_Angeles', dateStyle: 'medium', timeStyle: 'short' });
  const where = [cf.city, cf.region, cf.country].filter(Boolean).join(', ');
  const sourceLabel = SOURCE_LABELS[f.source] || f.source;

  const text = [
    `🌐 <b>New inquiry · dnnr.us</b>`,
    ``,
    `<b>Topic:</b> ${esc(f.topic)}`,
    `<b>Button:</b> ${esc(sourceLabel)}${f.button ? ` — “${esc(f.button)}”` : ''}`,
    `<b>Page:</b> ${esc((f.host || 'dnnr.us') + (f.page || '/'))}`,
    ``,
    `<b>Name:</b> ${esc(f.name)}`,
    `<b>Email:</b> <code>${esc(f.email)}</code>`,
    f.company ? `<b>Company:</b> ${esc(f.company)}` : null,
    ``,
    `<b>Message:</b>`,
    esc(f.message),
    ``,
    `<i>${esc(pt)} PT${where ? ` · ${esc(where)}` : ''}</i>`,
  ].filter((l) => l !== null).join('\n');

  const tg = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT_ID, text, parse_mode: 'HTML', disable_web_page_preview: true }),
  }).catch(() => null);

  if (!tg || !tg.ok) {
    return json(request, 502, { ok: false, error: "We couldn't send your message right now. Please try again, or email hello@dnnr.us." });
  }
  return json(request, 200, { ok: true });
}

export async function onRequest({ request }) {
  return json(request, 405, { ok: false, error: 'Method not allowed.' });
}
