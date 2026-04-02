import { auth0 } from "@/lib/auth0";
import ChatBox from "@/components/ChatBox";

export default async function Home() {
  const session = await auth0.getSession();

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center max-w-lg px-6 flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-2">PlanBot</h1>
        <p className="text-gray-400 mb-4">
          AI Day Planner — powered by Auth0 Token Vault
        </p>

        {session ? (
          <>
            <p className="text-green-400 mb-2 text-sm">
              Logged in as {session.user.email}
            </p>
            <a
              href="/api/connect-spotify"
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-block mb-4 text-sm"
            >
              Connect Spotify
            </a>
            <ChatBox />
            <a
              href="/auth/logout"
              className="text-sm text-gray-400 hover:text-white underline mt-4"
            >
              Sign out
            </a>
          </>
        ) : (
          <div>
            <a
              href="/auth/login"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-block"
            >
              Sign in with Auth0
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
