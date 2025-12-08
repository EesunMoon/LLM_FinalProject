export function ReviewsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-4">
        Your Reviews
      </h1>
      <p className="text-gray-400 mb-8">
        Rate and review movies to improve your recommendations.
      </p>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Search and add review */}
        <div className="p-8 border-2 border-dashed border-gray-700 rounded-lg">
          <p className="text-gray-500 text-center">
            🔍 Movie Search + Review Form
          </p>
        </div>

        {/* Review history */}
        <div className="p-8 border-2 border-dashed border-gray-700 rounded-lg">
          <p className="text-gray-500 text-center">
            📝 Your Review History
          </p>
        </div>
      </div>
    </div>
  );
}