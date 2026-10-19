type Context = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: Context) {
  const { path } = await context.params;
  const headers = new Headers();
  for (const name of ["cookie", "origin", "x-csrf-token", "content-type"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  // Keep the upstream fixed. Catch transport errors so callback codes never enter proxy error logs.
  // Tests use a distinct fixed loopback target; request content cannot choose a host/port.
  const backendPort = process.env.GHM_BROWSER_TEST === "main" ? 8016 : process.env.GHM_CORPUS_UI_TEST === "1" ? 8015 : 8000;
  const url = new URL(`http://127.0.0.1:${backendPort}/api/v1/` + path.map(encodeURIComponent).join("/"));
  url.search = new URL(request.url).search;
  try {
    const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer();
    if (body && body.byteLength > 1_048_576) return Response.json({ detail: "Request too large" }, { status: 413 });
    const response = await fetch(url, { method: request.method, headers, body, redirect: "manual",
      cache: "no-store", signal: AbortSignal.timeout(120_000) });
    const output = new Headers();
    for (const name of ["content-type", "content-disposition", "location", "cache-control", "referrer-policy", "x-content-type-options"]) {
      const value = response.headers.get(name);
      if (value) output.set(name, value);
    }
    for (const cookie of response.headers.getSetCookie()) output.append("set-cookie", cookie);
    return new Response(response.body, { status: response.status, headers: output });
  } catch {
    return Response.json({ detail: "Local backend unavailable or timed out; restart it and retry" },
      { status: 502, headers: { "Cache-Control": "no-store" } });
  }
}

export const GET = proxy;
export const POST = proxy;

export const PATCH = proxy;
export const PUT = proxy;
export const DELETE = proxy;
