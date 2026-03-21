// Catch-all proxy to backend for react-admin and other API calls
const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";

async function proxyRequest(request: Request, path: string): Promise<Response> {
  const url = new URL(request.url);
  const backendUrl = `${BACKEND}/api/${path}${url.search}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    try {
      init.body = await request.text();
    } catch {
      // No body
    }
  }

  const res = await fetch(backendUrl, init);
  const data = await res.text();

  return new Response(data, {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  });
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}
