import React from "react";
import { RotateCcw, Shield, FileCode2 } from "lucide-react";
import { translations } from "../i18n";

export default function Footer({ hasResult, onReset, lang }) {
  const t = translations[lang] || translations.en;
  const backendDocsUrl = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/docs`;

  const handleResetClick = () => {
    if (onReset) {
      onReset();
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="w-full mt-12 border-t border-slate-200/90 bg-white/70 backdrop-blur-xs py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 space-y-6">
        {/* "Try another message" Button - displayed when a result is active */}
        {hasResult && (
          <div className="flex justify-center pb-2">
            <button
              id="reset-analysis-btn"
              type="button"
              onClick={handleResetClick}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-xs sm:text-sm bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md shadow-blue-500/20 transition-all cursor-pointer active:scale-95"
            >
              <RotateCcw className="w-4 h-4" />
              <span>{t.resetBtn}</span>
            </button>
          </div>
        )}

        {/* Statutory Legal & Decision-Support Disclaimer */}
        <div
          id="statutory-disclaimer-box"
          className="p-4 sm:p-5 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-950 text-xs sm:text-sm leading-relaxed flex items-start gap-3"
        >
          <Shield className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-amber-900 block mb-0.5">
              {lang === "hi" ? "महत्वपूर्ण सूचना (Disclaimer):" : "Important Advisory:"}
            </span>
            <p className="text-amber-800">{t.disclaimer}</p>
          </div>
        </div>

        {/* Footer Links & Credits */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-slate-700">Satark (सतर्क)</span>
            <span>•</span>
            <span>Zero-Storage Scam Intelligence</span>
          </div>

          <div className="flex items-center gap-4">
            <a
              id="api-docs-link"
              href={backendDocsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-slate-600 hover:text-blue-600 transition-colors font-medium underline underline-offset-2"
            >
              <FileCode2 className="w-3.5 h-3.5" />
              <span>{t.docsLink}</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
