import { Auth0AI } from "@auth0/ai-vercel";
import { auth0 } from "../auth0";

const auth0AI = new Auth0AI();

// Helper to get the refresh token from the current session
export const getRefreshToken = async () => {
  const session = await auth0.getSession();
  return session?.tokenSet.refreshToken!;
};

// Google connection — Calendar + Tasks
export const withGoogle = auth0AI.withTokenVault({
  refreshToken: getRefreshToken,
  connection: "google-oauth2",
  scopes: [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks",
  ],
});

// Spotify connection — playback control + playlist access
export const withSpotify = auth0AI.withTokenVault({
  refreshToken: getRefreshToken,
  connection: "spotify",
  scopes: [
    "user-modify-playback-state",
    "user-read-playback-state",
    "playlist-read-private",
  ],
});

// Notion connection — read + write pages
export const withNotion = auth0AI.withTokenVault({
  refreshToken: getRefreshToken,
  connection: "notion",
  scopes: [],
});
