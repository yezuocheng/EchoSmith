export type TranscriptionLanguage = "auto" | "en" | "zh";

export const DEFAULT_TRANSCRIPTION_LANGUAGE: TranscriptionLanguage = "en";
export const TRANSCRIPTION_LANGUAGE_STORAGE_KEY = "echosmith.transcriptionLanguage";

function isTranscriptionLanguage(value: string | null): value is TranscriptionLanguage {
  return value === "auto" || value === "en" || value === "zh";
}

export function loadTranscriptionLanguage(): TranscriptionLanguage {
  try {
    const stored = window.localStorage.getItem(TRANSCRIPTION_LANGUAGE_STORAGE_KEY);
    return isTranscriptionLanguage(stored) ? stored : DEFAULT_TRANSCRIPTION_LANGUAGE;
  } catch {
    return DEFAULT_TRANSCRIPTION_LANGUAGE;
  }
}

export function saveTranscriptionLanguage(language: TranscriptionLanguage): void {
  try {
    window.localStorage.setItem(TRANSCRIPTION_LANGUAGE_STORAGE_KEY, language);
  } catch {
    // Transcription still works if storage is unavailable.
  }
}
