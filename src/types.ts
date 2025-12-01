export interface TopFactor {
  aspect?: string;
  description?: string;
  impact?: string;
}

export interface PredictionData {
  scope: string;
  date: string;
  theme?: string;
  summary?: { headline?: string; top_factors?: TopFactor[] };
  sections: Array<{
    title: string;
    rating?: number;
    highlights: string[];
    affirmation?: string;
    topic_scores?: Record<string, number>;
  }>;
  numerology?: NumerologyProfile;
  charts?: {
    natal?: {
      planets: Array<{ name: string; sign: string; degree: number; house: number }>;
    };
  };
  element?: string;
  sign?: string;
  life_path_number?: number;
  lucky_numbers?: number[];
  palette?: string[];
}

export interface NumerologyNumber {
  number: number;
  meaning: string;
}

export interface NumerologyProfile {
  core_numbers: {
    life_path: NumerologyNumber;
    expression: NumerologyNumber;
    soul_urge: NumerologyNumber;
    personality: NumerologyNumber;
    maturity?: NumerologyNumber;
  };
  cycles: {
    personal_year: NumerologyNumber;
    personal_month: NumerologyNumber;
    personal_day: NumerologyNumber;
  };
  pinnacles?: Array<{ number: number; meaning: string }>;
  challenges?: Array<{ number: number; meaning: string }>;
}

export interface CompatibilityResult {
  people: Array<{ name: string; dob: string }>;
  topic_scores: Record<string, number>;
  strengths: string[];
  challenges: string[];
  advice: string;
  numerology: {
    a: NumerologyProfile;
    b: NumerologyProfile;
  };
}

export interface NewProfileForm {
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  house_system?: string;
}

export interface SavedProfile {
  id: number;
  name: string;
  date_of_birth: string;
  time_of_birth?: string | null;
  place_of_birth?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  house_system?: string | null;
}
