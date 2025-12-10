import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { languages, type LanguageCode } from '../i18n';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = languages.find((l) => l.code === i18n.language) || languages[0];

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
          {languages.map((lang) => (
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
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
