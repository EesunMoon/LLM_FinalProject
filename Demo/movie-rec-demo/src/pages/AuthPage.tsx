export function AuthPage() {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-xl w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          Sign In to MovieRec
        </h1>
        
        {/* Placeholder for auth forms */}
        <div className="space-y-4">
          <div className="p-4 border-2 border-dashed border-gray-700 rounded-lg">
            <p className="text-gray-500 text-center text-sm">
              📧 Email/Password Form
            </p>
          </div>
          <div className="p-4 border-2 border-dashed border-gray-700 rounded-lg">
            <p className="text-gray-500 text-center text-sm">
              🔗 OAuth Buttons (Google, IMDB)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}