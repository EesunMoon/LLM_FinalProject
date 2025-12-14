import { VIBE_OPTIONS } from '../../types/user';

interface VibePickerProps {
  selectedVibes: string[];
  customText: string;
  onVibesChange: (vibes: string[]) => void;
  onCustomTextChange: (text: string) => void;
}

export function VibePicker({
  selectedVibes,
  customText,
  onVibesChange,
  onCustomTextChange,
}: VibePickerProps) {
  const toggleVibe = (vibeId: string) => {
    if (selectedVibes.includes(vibeId)) {
      onVibesChange(selectedVibes.filter((v) => v !== vibeId));
    } else {
      onVibesChange([...selectedVibes, vibeId]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Vibe chips */}
      <div className="flex flex-wrap gap-2">
        {VIBE_OPTIONS.map((vibe) => {
          const isSelected = selectedVibes.includes(vibe.id);
          return (
            <button
              key={vibe.id}
              onClick={() => toggleVibe(vibe.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                isSelected
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span className="mr-2">{vibe.emoji}</span>
              {vibe.label}
            </button>
          );
        })}
      </div>

      {/* Custom text input */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">
          Or describe in your own words:
        </label>
        <textarea
          value={customText}
          onChange={(e) => onCustomTextChange(e.target.value)}
          placeholder="I love movies where a ragtag group comes together and you see their chemistry grow over time..."
          rows={4}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-red-500 focus:outline-none resize-none"
        />
      </div>

      {/* Selection summary */}
      {selectedVibes.length > 0 && (
        <p className="text-sm text-gray-400">
          {selectedVibes.length} vibe{selectedVibes.length !== 1 ? 's' : ''} selected
        </p>
      )}
    </div>
  );
}