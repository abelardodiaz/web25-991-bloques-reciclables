const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ date: string }> }
) {
  const { date } = await params;
  const res = await fetch(`${BACKEND}/api/slots/${date}`);
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
