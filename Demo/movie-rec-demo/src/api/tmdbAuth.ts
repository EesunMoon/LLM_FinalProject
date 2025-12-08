const API_KEY = import.meta.env.VITE_TMDB_API_KEY;
const BASE_URL = 'https://api.themoviedb.org/3';

// Step 1: Creating the request token
export async function createRequestToken(): Promise<string> {
  const response = await fetch(
    `${BASE_URL}/authentication/token/new?api_key=${API_KEY}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to create request token');
  }
  
  const data = await response.json();
  return data.request_token;
}

// Step 2: Getting the URL to redirect user for authorization
export function getAuthorizationUrl(requestToken: string, redirectUrl: string): string {
  return `https://www.themoviedb.org/authenticate/${requestToken}?redirect_to=${encodeURIComponent(redirectUrl)}`;
}

// Step 3: Creating a session ID with the authorized request token
export async function createSession(requestToken: string): Promise<string> {
  const response = await fetch(
    `${BASE_URL}/authentication/session/new?api_key=${API_KEY}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_token: requestToken,
      }),
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  
  const data = await response.json();
  return data.session_id;
}

// Get account details using session ID
export async function getAccountDetails(sessionId: string) {
  const response = await fetch(
    `${BASE_URL}/account?api_key=${API_KEY}&session_id=${sessionId}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get account details');
  }
  
  return response.json();
}

// Get user's rated movies 
export async function getRatedMovies(accountId: number, sessionId: string) {
  const response = await fetch(
    `${BASE_URL}/account/${accountId}/rated/movies?api_key=${API_KEY}&session_id=${sessionId}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get rated movies');
  }
  
  return response.json();
}

// Get user's favorite movies
export async function getFavoriteMovies(accountId: number, sessionId: string) {
  const response = await fetch(
    `${BASE_URL}/account/${accountId}/favorite/movies?api_key=${API_KEY}&session_id=${sessionId}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get favorite movies');
  }
  
  return response.json();
}

// Get user's watchlist
export async function getWatchlist(accountId: number, sessionId: string) {
  const response = await fetch(
    `${BASE_URL}/account/${accountId}/watchlist/movies?api_key=${API_KEY}&session_id=${sessionId}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get watchlist');
  }
  
  return response.json();
}