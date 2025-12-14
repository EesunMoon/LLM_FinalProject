import { useState, useEffect, useRef } from 'react';
import { Search, X, Plus } from 'lucide-react';
import { searchMovies, getPosterUrl } from '../../api/tmdb';
import { type TMDBMovie } from '../../types/movie';
import { Spinner } from '../ui/Spinner';

interface MoviePickerProps {
  selectedIds: number[];
  onChange: (ids: number[]) => void;
  maxSelections?: number;
  placeholder?: string;
}

export function MoviePicker({
  selectedIds,
  onChange,
  maxSelections = 10,
  placeholder = 'Search for a movie...',
}: MoviePickerProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<TMDBMovie[]>([]);
  const [selectedMovies, setSelectedMovies] = useState<TMDBMovie[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.trim().length < 2) {
      setResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const movies = await searchMovies(query);
        // Filter out already selected movies
        const filtered = movies.filter((m) => !selectedIds.includes(m.id));
        setResults(filtered.slice(0, 8));
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, selectedIds]);

  // Fetch movie details for selected IDs on mount
  useEffect(() => {
    async function fetchSelectedMovies() {
      if (selectedIds.length === 0) {
        setSelectedMovies([]);
        return;
      }
      
      const movies = await Promise.all(
        selectedIds.map(async (id) => {
          try {
            const response = await fetch(
              `https://api.themoviedb.org/3/movie/${id}?api_key=${import.meta.env.VITE_TMDB_API_KEY}`
            );
            return response.json();
          } catch {
            return null;
          }
        })
      );
      setSelectedMovies(movies.filter(Boolean));
    }
    fetchSelectedMovies();
  }, [selectedIds]);

  const handleSelect = (movie: TMDBMovie) => {
    if (selectedIds.length >= maxSelections) return;
    onChange([...selectedIds, movie.id]);
    setSelectedMovies((prev) => [...prev, movie]);
    setQuery('');
    setResults([]);
    setShowResults(false);
  };

  const handleRemove = (movieId: number) => {
    onChange(selectedIds.filter((id) => id !== movieId));
    setSelectedMovies((prev) => prev.filter((m) => m.id !== movieId));
  };

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div ref={searchRef} className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowResults(true);
            }}
            onFocus={() => setShowResults(true)}
            placeholder={placeholder}
            disabled={selectedIds.length >= maxSelections}
            className="w-full bg-gray-800 text-white rounded-lg pl-10 pr-4 py-3 border border-gray-700 focus:border-red-500 focus:outline-none disabled:opacity-50"
          />
          {isSearching && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Spinner className="w-5 h-5" />
            </div>
          )}
        </div>

        {/* Search results dropdown */}
        {showResults && results.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
            {results.map((movie) => (
              <button
                key={movie.id}
                onClick={() => handleSelect(movie)}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-700 transition-colors text-left"
              >
                <img
                  src={getPosterUrl(movie.poster_path, 'w200')}
                  alt={movie.title}
                  className="w-10 h-14 object-cover rounded"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">{movie.title}</p>
                  <p className="text-gray-400 text-sm">
                    {movie.release_date?.split('-')[0] || 'TBA'}
                  </p>
                </div>
                <Plus className="w-5 h-5 text-gray-400" />
              </button>
            ))}
          </div>
        )}

        {/* No results message */}
        {showResults && query.length >= 2 && !isSearching && results.length === 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 p-4 text-center text-gray-400">
            No movies found for "{query}"
          </div>
        )}
      </div>

      {/* Selection count */}
      <p className="text-sm text-gray-400">
        {selectedIds.length} of {maxSelections} selected
      </p>

      {/* Selected movies grid */}
      {selectedMovies.length > 0 && (
        <div className="grid grid-cols-4 sm:grid-cols-5 gap-3">
          {selectedMovies.map((movie) => (
            <div key={movie.id} className="relative group">
              <img
                src={getPosterUrl(movie.poster_path, 'w200')}
                alt={movie.title}
                className="w-full aspect-[2/3] object-cover rounded-lg"
              />
              <button
                onClick={() => handleRemove(movie.id)}
                className="absolute -top-2 -right-2 w-6 h-6 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4 text-white" />
              </button>
              <p className="text-xs text-gray-400 mt-1 truncate">{movie.title}</p>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {selectedMovies.length === 0 && (
        <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center">
          <p className="text-gray-500">Search and select movies above</p>
        </div>
      )}
    </div>
  );
}