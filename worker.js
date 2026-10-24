// wacns.com site worker.
// wacns.com and www.wacns.com get the static site.
// Any other *.wacns.com host (one with no app of its own) gets the 404 page.
const SITE_HOSTS = new Set(["wacns.com", "www.wacns.com"]);

// Existing apps. Cloudflare routes exclude these hosts so this worker never
// runs for them; this list is a safety net that passes their traffic through
// untouched if that ever changes.
const APP_HOSTS = new Set([
  "rend.wacns.com",
  "rend-mcp.wacns.com",
  "rend-send.wacns.com",
  "thetower.wacns.com",
  "tower.wacns.com",
  "rdp.wacns.com",
]);

export default {
  async fetch(request, env) {
    const host = new URL(request.url).hostname.toLowerCase();

    if (SITE_HOSTS.has(host)) {
      return env.ASSETS.fetch(request);
    }

    if (APP_HOSTS.has(host)) {
      return fetch(request);
    }

    // Shared files the 404 page needs (styles, script, icon) load on any host
    const path = new URL(request.url).pathname;
    if (path.startsWith("/assets/") || path === "/favicon.svg") {
      return env.ASSETS.fetch(request);
    }

    const page = await env.ASSETS.fetch(new URL("/404.html", request.url));
    return new Response(page.body, { status: 404, headers: page.headers });
  },
};
