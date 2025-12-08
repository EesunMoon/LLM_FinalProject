import { useState } from 'react';
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';
import { StepIndicator } from './StepIndicator';
import { MoviePicker } from './MoviePicker';
import { VibePicker } from './VibePicker';
import { type OnboardingData, EMPTY_ONBOARDING } from '../../types/user';

interface OnboardingModalProps {
  onComplete: (data: OnboardingData) => void;
  onSkip: () => void;
}

const STEPS = [
  {
    title: "What have you watched recently?",
    subtitle: "Pick a few movies you've seen in the past few months",
  },
  {
    title: "What are your all-time favorites?",
    subtitle: "The movies you'd rewatch anytime",
  },
  {
    title: "What vibes do you love?",
    subtitle: "Help us understand your taste",
  },
];

export function OnboardingModal({ onComplete, onSkip }: OnboardingModalProps) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>(EMPTY_ONBOARDING);

  const canProceed = () => {
    switch (step) {
      case 1:
        return data.recentMovies.length > 0;
      case 2:
        return data.favoriteMovies.length > 0;
      case 3:
        return data.selectedVibes.length > 0 || data.customVibeText.trim().length > 0;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      onComplete(data);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />

      {/* Modal */}
      <div className="relative bg-gray-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-red-500" />
              <span className="text-lg font-semibold text-white">
                Set Up Your Taste Profile
              </span>
            </div>
            <span className="text-sm text-gray-400">
              Step {step} of {STEPS.length}
            </span>
          </div>
          <StepIndicator currentStep={step} totalSteps={STEPS.length} />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <h2 className="text-2xl font-bold text-white mb-2">
            {STEPS[step - 1].title}
          </h2>
          <p className="text-gray-400 mb-6">
            {STEPS[step - 1].subtitle}
          </p>

          {/* Step content */}
          {step === 1 && (
            <MoviePicker
              selectedIds={data.recentMovies}
              onChange={(ids) => setData({ ...data, recentMovies: ids })}
              maxSelections={8}
              placeholder="Search for movies you've watched recently..."
            />
          )}

          {step === 2 && (
            <MoviePicker
              selectedIds={data.favoriteMovies}
              onChange={(ids) => setData({ ...data, favoriteMovies: ids })}
              maxSelections={10}
              placeholder="Search for your all-time favorites..."
            />
          )}

          {step === 3 && (
            <VibePicker
              selectedVibes={data.selectedVibes}
              customText={data.customVibeText}
              onVibesChange={(vibes) => setData({ ...data, selectedVibes: vibes })}
              onCustomTextChange={(text) => setData({ ...data, customVibeText: text })}
            />
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-800 flex items-center justify-between">
          <div>
            {step > 1 ? (
              <button
                onClick={handleBack}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
                Back
              </button>
            ) : (
              <button
                onClick={onSkip}
                className="text-gray-400 hover:text-white transition-colors"
              >
                Skip for now
              </button>
            )}
          </div>

          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors"
          >
            {step === 3 ? 'Finish' : 'Next'}
            {step < 3 && <ChevronRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}