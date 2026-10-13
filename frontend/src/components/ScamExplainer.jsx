import React from "react";
import { Tag, HelpCircle, BookOpen, CheckCircle, AlertTriangle } from "lucide-react";
import { translations } from "../i18n";

export default function ScamExplainer({
  scamType,
  howItWorks,
  explanationEn,
  explanationHi,
  verdict,
  lang,
}) {
  const t = translations[lang] || translations.en;
  const isSafe = verdict === "Safe";

  // Select explanation based on active language toggle
  const activeExplanation = lang === "hi" && explanationHi ? explanationHi : explanationEn;

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-6 border border-slate-200 space-y-5">
      {/* Scam Category Badge */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Tag className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            {t.scamTypeHeading}:
          </span>
        </div>

        <div
          id="scam-type-badge"
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs sm:text-sm font-extrabold tracking-tight ${
            isSafe
              ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
              : "bg-rose-100 text-rose-900 border border-rose-300 shadow-2xs"
          }`}
        >
          {isSafe ? (
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
          )}
          <span>{scamType || (isSafe ? t.verdictSafe : "Scam")}</span>
        </div>
      </div>

      {/* "How this scam works" Box */}
      {howItWorks && (
        <div
          id="how-scam-works-box"
          className="p-4 rounded-xl bg-blue-50/60 border border-blue-200/80"
        >
          <div className="flex items-center gap-2 text-blue-900 font-bold text-xs sm:text-sm mb-1.5 font-heading">
            <BookOpen className="w-4 h-4 text-blue-600 shrink-0" />
            <span>{t.howItWorksHeading}</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-sans">
            {howItWorks}
          </p>
        </div>
      )}

      {/* Clear Explanation (Bilingual per toggle) */}
      {activeExplanation && (
        <div id="explanation-box" className="p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-xs sm:text-sm mb-1.5 font-heading">
            <HelpCircle className="w-4 h-4 text-slate-600 shrink-0" />
            <span>{t.explanationHeading}</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-sans">
            {activeExplanation}
          </p>
        </div>
      )}
    </div>
  );
}
