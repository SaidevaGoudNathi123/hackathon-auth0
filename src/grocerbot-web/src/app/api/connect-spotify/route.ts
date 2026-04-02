import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  // Log in via Spotify connection — Auth0 stores the Spotify tokens
  // on the user's identity, which we fetch via Management API
  return NextResponse.redirect(
    new URL("/auth/login?connection=spotify&returnTo=/", req.url)
  );
}
