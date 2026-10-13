import React from "react";
import { ShieldCheck, Lock, Globe } from "lucide-react";
import { translations } from "../i18n";

export default function Header({ lang, setLang }) {
  const t = translations[lang] || translations.en;

  const toggleLanguage = () => {
    setLang((prev) => (prev === "en" ? "hi" : "en"));
  };

  return (
    <header className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 transition-all">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between gap-3">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-sky-500 flex items-center justify-center shadow-md shadow-blue-500/20 text-white font-extrabold text-xl tracking-tight">
            <ShieldCheck className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 font-heading">
                {t.appTitle}
              </span>
              <span className="hidden xs:inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200 rounded-full">
                AI + Rules
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block font-medium">
              {t.tagline}
            </p>
          </div>
        </div>

        {/* Center / Privacy Guarantee Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <Lock className="w-3.5 h-3.5 text-emerald-600" />
          <span>{t.privacyBadge}</span>
        </div>

        {/* Right Action: Language Toggle */}
        <div className="flex items-center gap-2">
          {/* Mobile Privacy indicator */}
          <div className="md:hidden flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium" title={t.privacyBadge}>
            <Lock className="w-3 h-3 text-emerald-600" />
            <span className="truncate max-w-[90px]">{t.privacyShort}</span>
          </div>

          <button
            id="language-toggle-btn"
            type="button"
            onClick={toggleLanguage}
            aria-label={t.langAria}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200 transition-colors cursor-pointer active:scale-95 shadow-xs"
          >
            <Globe className="w-4 h-4 text-slate-600" />
            <span>{t.langToggle}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
