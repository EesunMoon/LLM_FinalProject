export function ProfilePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-4">
        Profile Settings
      </h1>

      <div className="bg-gray-900 rounded-xl p-6 max-w-2xl">
        <div className="space-y-6">
          {/* User info */}
          <div className="p-4 border-2 border-dashed border-gray-700 rounded-lg">
            <p className="text-gray-500 text-center text-sm">
              👤 User Avatar + Name
            </p>
          </div>

          {/* Connected accounts */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-3">
              Connected Accounts
            </h2>
            <div className="p-4 border-2 border-dashed border-gray-700 rounded-lg">
              <p className="text-gray-500 text-center text-sm">
                🔗 IMDB, Letterboxd, Google connections
              </p>
            </div>
          </div>

          {/* Preferences */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-3">
              Preferences
            </h2>
            <div className="p-4 border-2 border-dashed border-gray-700 rounded-lg">
              <p className="text-gray-500 text-center text-sm">
                ⚙️ Notification settings, genre preferences
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}