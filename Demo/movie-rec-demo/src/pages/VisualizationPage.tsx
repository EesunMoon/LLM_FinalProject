export function VisualizationPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-2">
        Your Taste Wrapped
      </h1>
      <p className="text-gray-400 mb-8">
        Discover insights about your movie preferences.
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Embedding visualization */}
        <div className="p-8 border-2 border-dashed border-gray-700 rounded-lg aspect-square">
          <p className="text-gray-500 text-center">
            📊 Taste Embedding Scatter Plot
          </p>
        </div>

        {/* Genre radar */}
        <div className="p-8 border-2 border-dashed border-gray-700 rounded-lg aspect-square">
          <p className="text-gray-500 text-center">
            🎯 Genre Preference Radar
          </p>
        </div>

        {/* Summary card */}
        <div className="md:col-span-2 p-8 border-2 border-dashed border-gray-700 rounded-lg">
          <p className="text-gray-500 text-center">
            ✨ "Your 2025 Movie Journey" Summary
          </p>
        </div>
      </div>
    </div>
  );
}