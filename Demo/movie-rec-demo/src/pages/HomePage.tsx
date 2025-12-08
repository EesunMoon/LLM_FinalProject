import { useState, useEffect } from 'react';
import { MovieCarousel } from '../components/movies/MovieCarousel';
import { MovieModal } from '../components/movies/MovieModal';
import { ChatToggle } from '../components/chat/ChatToggle';
import { ChatWindow } from '../components/chat/ChatWindow';
import { OnboardingModal } from '../components/onboarding/OnboardingModal';
import { mockRecommendationSets } from '../data/mockRecommendations';
import { type RecommendedMovie } from '../types/movie';
import { type OnboardingData } from '../types/user';

export function HomePage() {
  const [selectedMovie, setSelectedMovie] = useState<RecommendedMovie | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMovieContext, setChatMovieContext] = useState<RecommendedMovie | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingData = localStorage.getItem('onboardingData');
    const tmdbMovieData = localStorage.getItem('tmdbMovieData');
    
    // Show onboarding if:
    // - They haven't completed onboarding yet
    // - AND they don't have TMDB movie data (or have very little)
    if (!onboardingData) {
      const tmdbData = tmdbMovieData ? JSON.parse(tmdbMovieData) : null;
      const hasTMDBData = tmdbData && (
        tmdbData.ratedMovies?.length > 3 || 
        tmdbData.favoriteMovies?.length > 3
      );
      
      if (!hasTMDBData) {
        setShowOnboarding(true);
      }
    }
  }, []);

  const handleTalkToChat = () => {
    setChatMovieContext(selectedMovie);
    setIsChatOpen(true);
    setSelectedMovie(null);
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
    setChatMovieContext(null);
  };

  const handleChatToggle = () => {
    if (isChatOpen) {
      handleChatClose();
    } else {
      setChatMovieContext(null);
      setIsChatOpen(true);
    }
  };

  const handleOnboardingComplete = (data: OnboardingData) => {
    console.log('Onboarding complete:', data);
    localStorage.setItem('onboardingData', JSON.stringify(data));
    setShowOnboarding(false);
    
    // TODO: Send to your TasteEmbeddingGenerator backend
  };

  const handleOnboardingSkip = () => {
    // Mark as skipped so we don't show again
    localStorage.setItem('onboardingData', JSON.stringify({ skipped: true }));
    setShowOnboarding(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome Back!
        </h1>
        <p className="text-gray-400">
          Here are your personalized movie recommendations
        </p>
      </div>

      {/* Recommendation carousels */}
      {Object.entries(mockRecommendationSets).map(([key, { title, recommendations }]) => (
        <MovieCarousel
          key={key}
          title={title}
          recommendations={recommendations}
          onMovieClick={setSelectedMovie}
        />
      ))}

      {/* Movie detail modal */}
      {selectedMovie && (
        <MovieModal
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onTalkToChat={handleTalkToChat}
        />
      )}

      {/* Chat components */}
      <ChatToggle
        isOpen={isChatOpen}
        onClick={handleChatToggle}
      />
      {isChatOpen && (
        <ChatWindow
          onClose={handleChatClose}
          movieContext={chatMovieContext}
        />
      )}

      {/* Onboarding modal for new users */}
      {showOnboarding && (
        <OnboardingModal
          onComplete={handleOnboardingComplete}
          onSkip={handleOnboardingSkip}
        />
      )}
    </div>
  );
}