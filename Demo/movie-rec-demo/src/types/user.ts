export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  createdAt: Date;
  onboardingCompleted: boolean;
}

export interface OnboardingData {
  recentMovies: number[];      // TMDB movie IDs
  favoriteMovies: number[];    // TMDB movie IDs
  selectedVibes: string[];     // Preset vibe tags
  customVibeText: string;      // Free-form description
}

// Preset vibes for the picker
export const VIBE_OPTIONS = [
  { id: 'mind-bending', label: 'Mind-bending plot twists', emoji: '🌀' },
  { id: 'feel-good', label: 'Feel-good comfort watch', emoji: '☀️' },
  { id: 'ensemble', label: 'Ensemble cast with great chemistry', emoji: '👥' },
  { id: 'slow-burn', label: 'Slow burn & atmospheric', emoji: '🌙' },
  { id: 'visual', label: 'Visually stunning cinematography', emoji: '🎨' },
  { id: 'witty', label: 'Witty dialogue & banter', emoji: '💬' },
  { id: 'emotional', label: 'Emotional & moving', emoji: '🥲' },
  { id: 'action', label: 'Non-stop action & thrills', emoji: '💥' },
  { id: 'thought-provoking', label: 'Thought-provoking themes', emoji: '🧠' },
  { id: 'dark', label: 'Dark & gritty', emoji: '🖤' },
  { id: 'funny', label: 'Laugh-out-loud funny', emoji: '😂' },
  { id: 'romantic', label: 'Romantic & heartfelt', emoji: '💕' },
];

// Empty onboarding state
export const EMPTY_ONBOARDING: OnboardingData = {
  recentMovies: [],
  favoriteMovies: [],
  selectedVibes: [],
  customVibeText: '',
};