import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { PageLayout } from './components/layout/PageLayout';
import { HomePage } from './pages/HomePage';
import { AuthPage } from './pages/AuthPage';
import { ReviewsPage } from './pages/ReviewsPage';
import { VisualizationPage } from './pages/VisualizationPage';
import { ProfilePage } from './pages/ProfilePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth page without the standard layout */}
        <Route path="/auth" element={<AuthPage />} />

        {/* All other pages with header/layout */}
        <Route
          path="/"
          element={
            <PageLayout>
              <HomePage />
            </PageLayout>
          }
        />
        <Route
          path="/reviews"
          element={
            <PageLayout>
              <ReviewsPage />
            </PageLayout>
          }
        />
        <Route
          path="/visualization"
          element={
            <PageLayout>
              <VisualizationPage />
            </PageLayout>
          }
        />
        <Route
          path="/profile"
          element={
            <PageLayout>
              <ProfilePage />
            </PageLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;