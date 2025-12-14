import { type TasteProfile } from '../../api/visualization';

interface GenreRadarProps {
  profile: TasteProfile;
  comparisonProfile?: TasteProfile;
}

const RADAR_GENRES = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Thriller', 'Romance', 'Horror', 'Animation'];

export function GenreRadar({ profile, comparisonProfile }: GenreRadarProps) {
  const size = 300;
  const center = size / 2;
  const maxRadius = (size / 2) - 40;

  // Check if profile has any genre data
  const hasUserData = Object.values(profile.genreDistribution).some(v => v > 0);
  const hasComparisonData = comparisonProfile && Object.values(comparisonProfile.genreDistribution).some(v => v > 0);

  // Generate points for the radar polygon
  const getPolygonPoints = (genreDistribution: Record<string, number>) => {
    const maxValue = Math.max(...Object.values(genreDistribution), 1); // Avoid division by zero
    
    return RADAR_GENRES.map((genre, i) => {
      const angle = (Math.PI * 2 * i) / RADAR_GENRES.length - Math.PI / 2;
      const value = genreDistribution[genre] || 0;
      // Normalize to maxValue to fill the radar better
      const radius = (value / maxValue) * maxRadius * 0.9;
      const x = center + radius * Math.cos(angle);
      const y = center + radius * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  // Generate label positions
  const labelPositions = RADAR_GENRES.map((genre, i) => {
    const angle = (Math.PI * 2 * i) / RADAR_GENRES.length - Math.PI / 2;
    const x = center + (maxRadius + 25) * Math.cos(angle);
    const y = center + (maxRadius + 25) * Math.sin(angle);
    return { genre, x, y };
  });

  // Generate grid circles
  const gridCircles = [0.25, 0.5, 0.75, 1].map((ratio) => maxRadius * ratio);

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Genre Preferences</h3>
      
      <svg width={size} height={size} className="mx-auto">
        {/* Grid circles */}
        {gridCircles.map((radius, i) => (
          <circle
            key={i}
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#374151"
            strokeWidth="1"
          />
        ))}

        {/* Grid lines from center */}
        {RADAR_GENRES.map((_, i) => {
          const angle = (Math.PI * 2 * i) / RADAR_GENRES.length - Math.PI / 2;
          const x2 = center + maxRadius * Math.cos(angle);
          const y2 = center + maxRadius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="#374151"
              strokeWidth="1"
            />
          );
        })}

        {/* Comparison profile polygon (dashed, behind) */}
        {hasComparisonData && comparisonProfile && (
          <polygon
            points={getPolygonPoints(comparisonProfile.genreDistribution)}
            fill={`${comparisonProfile.color}20`}
            stroke={comparisonProfile.color}
            strokeWidth="2"
            strokeDasharray="5,5"
          />
        )}

        {/* User profile polygon (solid, on top) */}
        {hasUserData && (
          <polygon
            points={getPolygonPoints(profile.genreDistribution)}
            fill={`${profile.color}30`}
            stroke={profile.color}
            strokeWidth="2"
          />
        )}

        {/* Show message if no user data */}
        {!hasUserData && (
          <text
            x={center}
            y={center}
            textAnchor="middle"
            className="fill-gray-500 text-sm"
          >
            No genre data yet
          </text>
        )}

        {/* Labels */}
        {labelPositions.map(({ genre, x, y }) => (
          <text
            key={genre}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-gray-400 text-xs"
          >
            {genre}
          </text>
        ))}
      </svg>

      {/* Legend - always show user, conditionally show comparison */}
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: profile.color }} />
          <span className="text-sm text-gray-400">{profile.name}</span>
        </div>
        {comparisonProfile && (
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full border-2" 
              style={{ borderColor: comparisonProfile.color, borderStyle: 'dashed' }} 
            />
            <span className="text-sm text-gray-400">{comparisonProfile.name}</span>
          </div>
        )}
      </div>
    </div>
  );
}