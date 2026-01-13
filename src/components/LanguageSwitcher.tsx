import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { languages, type LanguageCode } from '../i18n';

// Translation completeness status for each language
// 'full' = 100% translated, 'partial' = UI translated but content English, 'minimal' = mostly English
const translationStatus: Record<LanguageCode, 'full' | 'partial' | 'minimal'> = {
  en: 'full',
  es: 'full',
  fr: 'full',
  ro: 'full',
  ne: 'partial', // Nepali has UI translated but some content may be English
};

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = languages.find((l) => l.code === i18n.language) || languages[0];
  const currentStatus = translationStatus[currentLang.code as LanguageCode] || 'partial';

  const handleSelect = (code: LanguageCode) => {
    i18n.changeLanguage(code);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="language-switcher" ref={dropdownRef}>
      <button
        type="button"
        className="language-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Select language"
      >
        <span className="lang-flag">{currentLang.flag}</span>
        <span className="lang-code">{currentLang.code.toUpperCase()}</span>
        {currentStatus !== 'full' && (
          <span
            className="lang-status-indicator"
            title={currentStatus === 'partial' ? 'Some content in English' : 'Mostly English'}
          >
            {currentStatus === 'partial' ? '◐' : '○'}
          </span>
        )}
        <svg
          className={`lang-chevron ${isOpen ? 'open' : ''}`}
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
        >
          <path
            d="M3 4.5L6 7.5L9 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <ul className="language-dropdown" role="listbox">
          {languages.map((lang) => {
            const status = translationStatus[lang.code as LanguageCode] || 'partial';
            return (
              <li key={lang.code}>
                <button
                  type="button"
                  className={`language-option ${lang.code === i18n.language ? 'active' : ''}`}
                  onClick={() => handleSelect(lang.code)}
                  role="option"
                  aria-selected={lang.code === i18n.language}
                >
                  <span className="lang-flag">{lang.flag}</span>
                  <span className="lang-name">{lang.name}</span>
                  {status !== 'full' && (
                    <span
                      className="lang-status-badge"
                      title={status === 'partial' ? 'Some content in English' : 'Mostly English'}
                    >
                      {status === 'partial' ? 'partial' : 'beta'}
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
