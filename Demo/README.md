# 🎬 ReelReason Demo - Frontend UI

This is the frontend demo for our LLM-Driven Conversational Movie Recommendation system. It provides a web interface showcasing personalized recommendations, explainability features, and the "Taste Wrapped" visualization.

## Tech Stack

- **React 19** + TypeScript
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Styling
- **React Router v7** - Navigation
- **Lucide React** - Icons

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** v18 or higher
- **npm** v9 or higher
- **TMDB API Key** (free)
- **OpenAI API Key** (requires billing)

Check your Node/npm versions:
```bash
node --version
npm --version
```

### Setup

1. **Navigate to the demo folder:**
   ```bash
   cd Demo/movie-rec-demo
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   ```bash
   touch .env
   ```
   
   Add your API keys (see [API Setup](#-api-setup) below):
   ```env
   VITE_TMDB_API_KEY=<your_tmdb_api_key_here>
   VITE_OPENAI_API_KEY=<your_openai_api_key_here>
   ```
   
   **⚠️ IMPORTANT:** Never commit your `.env` file to version control. It's already in `.gitignore`.

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   The terminal will show a local URL (usually http://localhost:5173). Open it in your browser.

---

## 🔑 API Setup

The demo requires two API keys to function:

### 1. TMDB API Key (Required)

**What it's for:** Fetching movie metadata, posters, and user authentication via TMDB OAuth.

**Steps to get your key:**

1. **Create a TMDB account:**
   - Go to https://www.themoviedb.org/signup
   - Sign up with email or social login

2. **Request an API key:**
   - Visit https://www.themoviedb.org/settings/api
   - Click "Request an API Key"
   - Choose "Developer" (not commercial)
   - Accept the terms

3. **Fill out the application:**
   - Application Name: `ReelReason Demo` (or any name)
   - Application URL: `http://localhost:5173`
   - Application Summary: `Movie recommendation system for academic project`

4. **Copy your API Key (v3 auth):**
   - Once approved (instant), you'll see your API Key
   - Copy the "API Key" (not the "API Read Access Token")

5. **Add to `.env`:**
   ```env
   VITE_TMDB_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

**Free tier limits:** 
- 40 requests per 10 seconds
- Sufficient for development and demos

---

### 2. OpenAI API Key (Required)

**What it's for:** Generating personalized movie recommendations and explanations using GPT-4o-mini.

**Steps to get your key:**

1. **Create an OpenAI account:**
   - Go to https://platform.openai.com/signup
   - Sign up with email or Google/Microsoft

2. **Add billing information:**
   - Go to https://platform.openai.com/account/billing
   - Click "Add payment method"
   - Add a credit/debit card (required even for free tier usage)
   - Set a usage limit (recommended: $5-10 for testing)

3. **Create an API key:**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it (e.g., "ReelReason Demo")
   - Copy the key immediately (you won't see it again!)

4. **Add to `.env`:**
   ```env
   VITE_OPENAI_API_KEY=sk-proj-abc123xyz789...
   ```

**Cost estimates:**
- Embedding generation: ~$0.02 per 1,000 users
- GPT-4o-mini recommendations: ~$0.15 per 1,000 requests
- Typical demo session: $0.01-0.05
- Budget $5 for extensive testing
---

## 📁 Project Structure

```
movie-rec-demo/
├── .env                         # API keys (DO NOT COMMIT)
├── .env.example                 # Template for API keys
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Router setup with all routes
│   ├── index.css                # Tailwind imports + base styles
│   │
│   ├── api/
│   │   ├── tmdb.ts              # TMDB API calls
│   │   ├── tmdbAuth.ts          # TMDB OAuth flow
│   │   └── recommendations.ts   # OpenAI recommendation generation
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx       # Top navigation bar
│   │   │   └── PageLayout.tsx   # Page wrapper with header
│   │   ├── auth/
│   │   │   └── OAuthButtons.tsx # TMDB/Google OAuth
│   │   ├── movies/
│   │   │   ├── MovieCard.tsx    # Movie poster + info
│   │   │   └── MovieCarousel.tsx # Horizontal scroll container
│   │   └── reviews/
│   │       └── ReviewCard.tsx   # User review display
│   │
│   ├── context/
│   │   └── AuthContext.tsx      # User authentication state
│   │
│   └── pages/
│       ├── AuthPage.tsx         # Sign in / OAuth
│       ├── TMDBCallbackPage.tsx # OAuth callback handler
│       ├── PersonalizingPage.tsx # Loading screen with pipeline
│       ├── HomePage.tsx         # Recommendations + Chat
│       ├── ReviewsPage.tsx      # Manual review entry
│       ├── VisualizationPage.tsx # Taste Wrapped visualizations
│       └── ProfilePage.tsx      # User settings
│
├── index.html
├── package.json
├── vite.config.ts
├── postcss.config.js
└── tailwind.config.js
```

---

## 📄 Pages Overview

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Recommendation carousels with "Because you loved..." explanations |
| `/auth` | Auth | TMDB OAuth login |
| `/auth/tmdb/callback` | OAuth Callback | Handles TMDB authentication |
| `/personalizing` | Personalizing | Shows pipeline: embedding → search → recommendations |
| `/reviews` | Reviews | Rate movies, see history, update recommendations |
| `/visualization` | Taste Wrapped | 2D taste map, genre radar, AI summary |
| `/profile` | Profile | Account settings (coming soon) |

---

## 🛠 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with hot reload |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

---

## 🎨 Styling Notes

We're using **Tailwind CSS v4**, which has a simplified setup:
- No `tailwind.config.js` needed for basic usage
- Just `@import "tailwindcss";` in `index.css`
- Uses the `@tailwindcss/postcss` plugin

Dark theme colors we're using:
- Background: `bg-gray-950` (darkest), `bg-gray-900` (cards)
- Text: `text-white`, `text-gray-400` (secondary)
- Accent: `text-red-600`, `bg-red-600` (buttons, highlights)

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required - TMDB API for movie data and OAuth
VITE_TMDB_API_KEY=your_tmdb_api_key_here

# Required - OpenAI API for recommendations
VITE_OPENAI_API_KEY=your_openai_api_key_here

# Optional - Google OAuth (not yet implemented)
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

We've included a `.env.example` file as a template. Copy it:
```bash
cp .env.example .env
```
Then fill in your actual API keys.

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test locally with `npm run dev`
4. Push and create a PR

### Adding New Components

Components go in `src/components/` organized by feature:
- `layout/` - Header, Footer, PageLayout
- `movies/` - MovieCard, MovieCarousel, MovieModal
- `chat/` - ChatWindow, ChatMessage, ChatInput
- `visualization/` - Charts and Taste Wrapped components
- `auth/` - Login forms, OAuth buttons
- `reviews/` - Review cards, review form

### Adding New Pages

1. Create the page in `src/pages/YourPage.tsx`
2. Add the route in `src/App.tsx`
3. Add nav link in `src/components/layout/Header.tsx` if needed

---

## 📝 Features Implemented

### Core Features
- ✅ TMDB OAuth authentication
- ✅ Movie search and selection
- ✅ Personalized recommendation generation via OpenAI
- ✅ "Because you loved..." explanations
- ✅ Movie review system with rating slider
- ✅ Real-time taste profile updates
- ✅ Taste Wrapped visualization (2D map, genre radar, AI summary)
- ✅ Recommendation update pipeline visualization

### Coming Soon
- [ ] Conversational chat interface
- [ ] Profile settings page
- [ ] Social features (friend comparisons)
- [ ] Watchlist management
- [ ] Mobile-responsive improvements

---

## ❓ Troubleshooting

### Port already in use
```bash
npm run dev -- --port 3000
```

### Dependencies issues
```bash
rm -rf node_modules package-lock.json
npm install
```

### Tailwind not working
Make sure `@tailwindcss/postcss` is installed and `postcss.config.js` exists.

### TMDB OAuth not working
- Check that your API key is correct in `.env`
- Verify the callback URL is set to `http://localhost:5173/auth/tmdb/callback` in TMDB settings
- Clear browser cookies and try again

### OpenAI API errors
- **"Incorrect API key"**: Check your key in `.env`, ensure it starts with `sk-proj-`
- **"Rate limit exceeded"**: Wait a moment and try again
- **"Insufficient quota"**: Add billing information in OpenAI dashboard
- **"Model not found"**: Ensure you have access to GPT-4o-mini

### No recommendations showing
- Check browser console for API errors
- Verify both API keys are in `.env`
- Make sure you've completed onboarding or have TMDB account with ratings
- Try clearing localStorage: `localStorage.clear()` in browser console

---

## 📖 Additional Documentation

- [TMDB API Documentation](https://developer.themoviedb.org/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [React Router v7 Docs](https://reactrouter.com/)
- [Tailwind CSS v4 Docs](https://tailwindcss.com/docs)

---

## 📄 License

This project is part of an academic assignment for COMS 6998: Introduction to LLM-based Generative AI Systems at Columbia University.

---

## 🙏 Acknowledgments

- **TMDB** for the movie database API
- **OpenAI** for GPT-4o-mini and embedding models
- **MovieLens** for datasets
- Course instructors and TAs for guidance