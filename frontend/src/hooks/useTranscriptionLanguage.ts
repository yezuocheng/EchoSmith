import { useCallback, useState } from "react";

import {
  loadTranscriptionLanguage,
  saveTranscriptionLanguage,
  type TranscriptionLanguage,
} from "../lib/transcriptionLanguage";

export function useTranscriptionLanguage(): [
  TranscriptionLanguage,
  (language: TranscriptionLanguage) => void,
] {
  const [language, setLanguage] = useState<TranscriptionLanguage>(loadTranscriptionLanguage);

  const updateLanguage = useCallback((nextLanguage: TranscriptionLanguage) => {
    saveTranscriptionLanguage(nextLanguage);
    setLanguage(nextLanguage);
  }, []);

  return [language, updateLanguage];
}
