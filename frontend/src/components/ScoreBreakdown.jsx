import React from "react";
import { Sliders, AlertTriangle, ShieldCheck, Cpu, Scale } from "lucide-react";
import { translations } from "../i18n";

export default function ScoreBreakdown({
  scoreBreakdown,
  redFlags = [],
  aiAvailable = true,
  lang,
}) {
  const t = translations[lang] || translations.en;
  const rulesScore = scoreBreakdown?.rules ?? 0;
  const aiScore = scoreBreakdown?.ai ?? null;

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-6 border border-slate-200 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 text-slate-800 font-bold text-sm sm:text-base font-heading">
        <Sliders className="w-4 h-4 text-blue-600" />
        <span>{t.scoreBreakdownHeading}</span>
      </div>

      {/* Dual Comparative Progress Bars */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Rules Contribution Bar */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
              <Scale className="w-3.5 h-3.5 text-indigo-600" />
              {t.rulesContrib}
            </span>
            <span className="text-xs font-extrabold text-slate-900 bg-white px-2 py-0.5 rounded-md border border-slate-200">
              {rulesScore} / 100
            </span>
          </div>
          <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${Math.min(100, Math.max(0, rulesScore))}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            {aiAvailable
              ? lang === "hi"
                ? "कुल स्कोर में 40% योगदान"
                : "Contributes 40% weight to risk score"
              : lang === "hi"
                ? "AI अनुपलब्ध होने पर 100% योगदान"
                : "Active 100% weight (AI unavailable)"}
          </p>
        </div>

        {/* AI Contribution Bar */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
              <Cpu className="w-3.5 h-3.5 text-blue-600" />
              {t.aiContrib}
            </span>
            <span className="text-xs font-extrabold text-slate-900 bg-white px-2 py-0.5 rounded-md border border-slate-200">
              {aiAvailable && aiScore !== null ? `${aiScore} / 100` : "N/A"}
            </span>
          </div>
          <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-1000 ease-out ${
                aiAvailable && aiScore !== null ? "bg-blue-600" : "bg-slate-300"
              }`}
              style={{
                width:
                  aiAvailable && aiScore !== null
                    ? `${Math.min(100, Math.max(0, aiScore))}%`
                    : "0%",
              }}
            />
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            {aiAvailable && aiScore !== null
              ? lang === "hi"
                ? "कुल स्कोर में 60% योगदान (Gemini AI)"
                : "Contributes 60% weight (Gemini AI)"
              : lang === "hi"
                ? "AI मॉडल ऑफलाइन (केवल नियम लागू)"
                : "AI offline (rule engine fallback active)"}
          </p>
        </div>
      </div>

      {/* Red Flags Chips */}
      <div>
        <div className="flex items-center gap-2 mb-2.5">
          <AlertTriangle className="w-4 h-4 text-rose-500" />
          <h3 className="text-xs sm:text-sm font-bold text-slate-800">
            {t.redFlagsHeading}
          </h3>
        </div>

        {redFlags && redFlags.length > 0 && redFlags[0] !== "No red flags detected" ? (
          <div className="flex flex-wrap gap-2">
            {redFlags.map((flag, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-rose-50 border border-rose-200 text-rose-800 shadow-2xs"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
                {flag}
              </span>
            ))}
          </div>
        ) : (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 border border-emerald-200 text-emerald-800">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>
              {lang === "hi"
                ? "संदेश में कोई बड़ा खतरा नहीं पाया गया"
                : "No critical red flags detected in this message"}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
