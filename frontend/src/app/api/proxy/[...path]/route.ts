import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, ""); // elimina la barra final si existe

/**
 * Proxy para peticiones GET
 */
export async function GET(
    req: Request,
    context: { params: Promise<{ path: string[] }> }
) {
    const { path } = await context.params;
    const search = new URL(req.url).search;

    const targetPath = path.join("/");
    const backendUrl = `${API_BASE}/${targetPath}${search}`;


    try {
        const res = await fetch(backendUrl, { method: "GET" });
        const text = await res.text();
        return new NextResponse(text, { status: res.status });
    } catch (error) {
        return NextResponse.json({ error: "Proxy GET error" }, { status: 500 });
    }
}

/**
 * Proxy para peticiones POST
 */
export async function POST(
    req: Request,
    context: { params: Promise<{ path: string[] }> }
) {
    const { path } = await context.params;
    const targetPath = path.join("/");

    const backendUrl = `${API_BASE}/${targetPath}/`;


    try {
        const body = await req.text();

        const res = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": req.headers.get("Content-Type") || "application/json",
            },
            body,
        });

        const text = await res.text();
        return new NextResponse(text, { status: res.status });
    } catch (error) {
        return NextResponse.json({ error: "Proxy POST error" }, { status: 500 });
    }
}
