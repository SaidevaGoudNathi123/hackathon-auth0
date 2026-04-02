import { tool } from "ai";
import { z } from "zod/v3";
import { getAccessTokenFromTokenVault } from "@auth0/ai-vercel";
import { withSpotify } from "../auth/token-vault";

const SPOTIFY_API = "https://api.spotify.com/v1";

// Tool: Play a playlist by mood/genre
export const playPlaylist = withSpotify(
  tool({
    description:
      "Search for and play a Spotify playlist based on a mood or genre. Examples: 'deep focus', 'lofi beats', 'morning energy'.",
    parameters: z.object({
      query: z
        .string()
        .describe("Mood or genre to search for (e.g., 'deep focus', 'workout', 'lo-fi')"),
    }),
    execute: async ({ query }) => {
      const accessToken = getAccessTokenFromTokenVault();

      // Search for playlists
      const searchRes = await fetch(
        `${SPOTIFY_API}/search?q=${encodeURIComponent(query)}&type=playlist&limit=3`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      if (!searchRes.ok) {
        throw new Error(`Spotify search error: ${searchRes.status}`);
      }

      const searchData = await searchRes.json();
      const playlists = searchData.playlists?.items;

      if (!playlists || playlists.length === 0) {
        return { error: `No playlists found for "${query}".` };
      }

      const chosen = playlists[0];

      // Start playback
      const playRes = await fetch(`${SPOTIFY_API}/me/player/play`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ context_uri: chosen.uri }),
      });

      if (playRes.status === 404) {
        return {
          success: false,
          playlist: chosen.name,
          playlistUrl: chosen.external_urls?.spotify,
          message: `Found "${chosen.name}" but no active Spotify device. Open Spotify first.`,
        };
      }

      return {
        success: true,
        playlist: chosen.name,
        trackCount: chosen.tracks?.total || 0,
        playlistUrl: chosen.external_urls?.spotify,
        message: `Now playing: "${chosen.name}" (${chosen.tracks?.total} tracks)`,
      };
    },
  })
);

// Tool: Get currently playing track
export const getNowPlaying = withSpotify(
  tool({
    description: "Get the currently playing track on the user's Spotify.",
    parameters: z.object({
      _check: z.string().optional().describe("Not used"),
    }),
    execute: async () => {
      const accessToken = getAccessTokenFromTokenVault();

      const response = await fetch(`${SPOTIFY_API}/me/player/currently-playing`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (response.status === 204) {
        return { playing: false, message: "Nothing is currently playing." };
      }

      if (!response.ok) {
        throw new Error(`Spotify API error: ${response.status}`);
      }

      const data = await response.json();

      return {
        playing: data.is_playing,
        track: data.item?.name,
        artist: data.item?.artists?.map((a: any) => a.name).join(", "),
        album: data.item?.album?.name,
        message: data.is_playing
          ? `Now playing: "${data.item?.name}" by ${data.item?.artists?.map((a: any) => a.name).join(", ")}`
          : "Playback is paused.",
      };
    },
  })
);

// Tool: Pause/resume playback
export const togglePlayback = withSpotify(
  tool({
    description: "Pause or resume Spotify playback.",
    parameters: z.object({
      action: z.enum(["pause", "resume"]).describe("Whether to pause or resume playback"),
    }),
    execute: async ({ action }) => {
      const accessToken = getAccessTokenFromTokenVault();

      const endpoint =
        action === "pause"
          ? `${SPOTIFY_API}/me/player/pause`
          : `${SPOTIFY_API}/me/player/play`;

      const response = await fetch(endpoint, {
        method: "PUT",
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (response.status === 404) {
        return { success: false, message: "No active Spotify device found. Open Spotify first." };
      }

      return {
        success: true,
        message: action === "pause" ? "Playback paused." : "Playback resumed.",
      };
    },
  })
);
