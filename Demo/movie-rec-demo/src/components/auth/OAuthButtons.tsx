import { Chrome } from 'lucide-react';

interface OAuthButtonsProps {
  onGoogleClick: () => void;
  onTMDBClick: () => void;
}

export function OAuthButtons({ onGoogleClick, onTMDBClick }: OAuthButtonsProps) {
  return (
    <div className="space-y-3">
      {/* Google */}
      <button
        onClick={onGoogleClick}
        className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-100 text-gray-900 font-medium py-3 px-4 rounded-lg transition-colors"
      >
        <Chrome className="w-5 h-5" />
        Continue with Google
      </button>

      {/* TMDB */}
      <button
        onClick={onTMDBClick}
        className="w-full flex items-center justify-center gap-3 bg-[#0d253f] hover:bg-[#1a3a5c] text-white font-medium py-3 px-4 rounded-lg transition-colors"
      >
        <img 
          src="/tmdb-logo.png" 
          alt="TMDB" 
          className="w-5 h-5 object-contain"
        />
        Continue with TMDB
      </button>
    </div>
  );
}