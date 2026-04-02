import OpenAI from "openai";
import { auth0 } from "@/lib/auth0";

const openaiClient = new OpenAI();

const SYSTEM_PROMPT = `You are PlanBot, an AI day planner assistant.

You can control the user's Spotify:
- Play playlists by mood (deep focus, lofi, workout, etc.)
- Check what's currently playing
- Pause or resume playback

If a tool needs authorization, tell the user and provide the auth link.
Be concise and friendly.`;

// Tool definitions for OpenAI
const TOOLS: OpenAI.Chat.Completions.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "playPlaylist",
      description:
        "Search for and play a Spotify playlist based on a mood or genre.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Mood or genre (e.g., 'deep focus', 'lofi', 'workout')",
          },
        },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "getNowPlaying",
      description: "Get the currently playing track on Spotify.",
      parameters: {
        type: "object",
        properties: {},
      },
    },
  },
  {
    type: "function",
    function: {
      name: "togglePlayback",
      description: "Pause or resume Spotify playback.",
      parameters: {
        type: "object",
        properties: {
          action: {
            type: "string",
            enum: ["pause", "resume"],
            description: "Whether to pause or resume",
          },
        },
        required: ["action"],
      },
    },
  },
];

const SPOTIFY_API = "https://api.spotify.com/v1";

// Tool execution functions
async function executePlayPlaylist(
  args: { query: string },
  accessToken: string
) {
  const searchRes = await fetch(
    `${SPOTIFY_API}/search?q=${encodeURIComponent(args.query)}&type=playlist&limit=3`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );

  if (!searchRes.ok) {
    return { error: `Spotify search failed: ${searchRes.status}` };
  }

  const data = await searchRes.json();
  const playlists = data.playlists?.items;

  if (!playlists?.length) {
    return { error: `No playlists found for "${args.query}".` };
  }

  const chosen = playlists[0];

  // Try to start playback
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
      playlist: chosen.name,
      url: chosen.external_urls?.spotify,
      message: `Found "${chosen.name}" but no active Spotify device. Open Spotify on your phone or computer first!`,
    };
  }

  return {
    playlist: chosen.name,
    tracks: chosen.tracks?.total,
    url: chosen.external_urls?.spotify,
    message: `Now playing "${chosen.name}" (${chosen.tracks?.total} tracks)`,
  };
}

async function executeGetNowPlaying(accessToken: string) {
  const res = await fetch(`${SPOTIFY_API}/me/player/currently-playing`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (res.status === 204) {
    return { playing: false, message: "Nothing is currently playing." };
  }

  if (!res.ok) {
    return { error: `Spotify API error: ${res.status}` };
  }

  const data = await res.json();
  return {
    playing: data.is_playing,
    track: data.item?.name,
    artist: data.item?.artists?.map((a: any) => a.name).join(", "),
    album: data.item?.album?.name,
  };
}

async function executeTogglePlayback(
  args: { action: string },
  accessToken: string
) {
  const endpoint =
    args.action === "pause"
      ? `${SPOTIFY_API}/me/player/pause`
      : `${SPOTIFY_API}/me/player/play`;

  const res = await fetch(endpoint, {
    method: "PUT",
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (res.status === 404) {
    return { error: "No active Spotify device found. Open Spotify first." };
  }

  return {
    message: args.action === "pause" ? "Playback paused." : "Playback resumed.",
  };
}

// Get Management API token via client credentials
async function getManagementToken(): Promise<string> {
  const res = await fetch(`https://${process.env.AUTH0_DOMAIN}/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.AUTH0_CLIENT_ID,
      client_secret: process.env.AUTH0_CLIENT_SECRET,
      audience: `https://${process.env.AUTH0_DOMAIN}/api/v2/`,
      grant_type: "client_credentials",
    }),
  });

  if (!res.ok) {
    throw new Error(`Management API token error: ${res.status}`);
  }

  const data = await res.json();
  return data.access_token;
}

// Get Spotify token via Auth0 Management API (reads IdP tokens from user identity)
async function getSpotifyToken(userId: string): Promise<string> {
  const mgmtToken = await getManagementToken();

  const res = await fetch(
    `https://${process.env.AUTH0_DOMAIN}/api/v2/users/${encodeURIComponent(userId)}?fields=identities&include_fields=true`,
    { headers: { Authorization: `Bearer ${mgmtToken}` } }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch user identities: ${res.status} ${text}`);
  }

  const user = await res.json();
  const spotifyIdentity = user.identities?.find(
    (id: any) => id.connection === "spotify"
  );

  if (!spotifyIdentity?.access_token) {
    throw new Error(
      "CONNECT_SPOTIFY: No Spotify identity linked. Please click 'Connect Spotify' to link your account."
    );
  }

  return spotifyIdentity.access_token;
}

export async function POST(req: Request) {
  try {
    const session = await auth0.getSession();
    if (!session) {
      return new Response("Unauthorized", { status: 401 });
    }

    const { messages } = await req.json();

    // Call OpenAI with tools
    const chatMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: "system", content: SYSTEM_PROMPT },
      ...messages,
    ];

    const response = await openaiClient.chat.completions.create({
      model: "gpt-4o-mini",
      messages: chatMessages,
      tools: TOOLS,
    });

    const choice = response.choices[0].message;

    // If no tool calls, return the text response
    if (!choice.tool_calls?.length) {
      return new Response(choice.content || "I'm not sure how to help with that.", {
        headers: { "Content-Type": "text/plain" },
      });
    }

    // Execute tool calls
    const toolResults: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [];

    for (const toolCall of choice.tool_calls) {
      const args = JSON.parse(toolCall.function.arguments);
      let result: any;

      try {
        // Get Spotify token via Auth0 Management API
        const spotifyToken = await getSpotifyToken(session.user.sub);

        switch (toolCall.function.name) {
          case "playPlaylist":
            result = await executePlayPlaylist(args, spotifyToken);
            break;
          case "getNowPlaying":
            result = await executeGetNowPlaying(spotifyToken);
            break;
          case "togglePlayback":
            result = await executeTogglePlayback(args, spotifyToken);
            break;
          default:
            result = { error: `Unknown tool: ${toolCall.function.name}` };
        }
      } catch (err: any) {
        // Return Token Vault errors directly so we can see them
        if (err.message.includes("Token Vault") || err.message.includes("CONNECT_SPOTIFY") || err.message.includes("refresh token")) {
          return new Response(err.message, {
            headers: { "Content-Type": "text/plain" },
          });
        }
        result = { error: err.message };
      }

      toolResults.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: JSON.stringify(result),
      });
    }

    // Send tool results back to get final response
    const finalResponse = await openaiClient.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        ...chatMessages,
        choice,
        ...toolResults,
      ],
    });

    const finalText =
      finalResponse.choices[0].message.content || "Done!";

    return new Response(finalText, {
      headers: { "Content-Type": "text/plain" },
    });
  } catch (error: any) {
    console.error("Chat API error:", error);
    return new Response(
      `Error: ${error.message || "Internal server error"}`,
      { status: 500, headers: { "Content-Type": "text/plain" } }
    );
  }
}
