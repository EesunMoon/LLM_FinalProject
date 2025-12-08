export function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-4">
        Welcome Back!
      </h1>
      <p className="text-gray-400">
        Your personalized movie recommendations will appear here.
      </p>
      
      {/* Placeholder for recommendation carousel */}
      <div className="mt-8 p-8 border-2 border-dashed border-gray-700 rounded-lg">
        <p className="text-gray-500 text-center">
          🎬 Recommendation Carousel Coming Soon
        </p>
      </div>
    </div>
  );
}