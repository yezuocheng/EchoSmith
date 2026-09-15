import type { ChangeEvent } from "react";

import type { TranscriptionLanguage } from "../lib/transcriptionLanguage";

interface LanguageSelectorProps {
  value: TranscriptionLanguage;
  onChange: (language: TranscriptionLanguage) => void;
  disabled?: boolean;
}

export function LanguageSelector({
  value,
  onChange,
  disabled = false,
}: LanguageSelectorProps): JSX.Element {
  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onChange(event.target.value as TranscriptionLanguage);
  };

  return (
    <div>
      <label
        htmlFor="transcription-language"
        className="text-sm font-medium text-gray-900 dark:text-white mb-2 block"
      >
        转写语言
      </label>
      <select
        id="transcription-language"
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className="w-full rounded-lg border border-black/[0.08] dark:border-white/[0.08] bg-white/70 dark:bg-zinc-800/70 px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
      >
        <option value="en">English（英文录音推荐）</option>
        <option value="auto">自动检测</option>
        <option value="zh">中文</option>
      </select>
    </div>
  );
}
