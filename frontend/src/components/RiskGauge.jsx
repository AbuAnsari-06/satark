import React, { useEffect, useState } from "react";
import { ShieldCheck, AlertTriangle, ShieldAlert, Info } from "lucide-react";
import { translations } from "../i18n";

export default function RiskGauge({ verdict, riskScore, aiAvailable, lang }) {
  const t = translations[lang] || translations.en;
  const [animatedOffset, setAnimatedOffset] = useState(276.46);

  // SVG circle calculations
  const radius = 44;
  const circumference = 2 * Math.PI * radius; // ~276.46

  useEffect(() => {
    // Trigger smooth stroke-dashoffset transition after mount
    const timer = setTimeout(() => {
      const targetOffset = circumference - (circumference * Math.min(100, Math.max(0, riskScore))) / 100;
      setAnimatedOffset(targetOffset);
    }, 100);

    return () => clearTimeout(timer);
  }, [riskScore, circumference]);

  // Styling attributes based on verdict
  const getTheme = () => {
    if (verdict === "Safe") {
      return {
        badgeBg: "bg-emerald-50 border-emerald-200 text-emerald-800",
        stroke: "#10b981", // Emerald 500
        textColor: "text-emerald-700",
        verdictTitle: t.verdictSafe,
        verdictDesc: t.verdictDescSafe,
        icon: <ShieldCheck className="w-8 h-8 text-emerald-600 shrink-0" strokeWidth={2.2} />,
      };
    }
    if (verdict === "Suspicious") {
      return {
        badgeBg: "bg-amber-50 border-amber-200 text-amber-800",
        stroke: "#f59e0b", // Amber 500
        textColor: "text-amber-700",
        verdictTitle: t.verdictSuspicious,
        verdictDesc: t.verdictDescSuspicious,
        icon: <AlertTriangle className="w-8 h-8 text-amber-600 shrink-0" strokeWidth={2.2} />,
      };
    }
    // Likely Scam
    return {
      badgeBg: "bg-rose-50 border-rose-200 text-rose-800",
      stroke: "#ef4444", // Rose 500
      textColor: "text-rose-700",
      verdictTitle: t.verdictScam,
      verdictDesc: t.verdictDescScam,
      icon: <ShieldAlert className="w-8 h-8 text-rose-600 shrink-0" strokeWidth={2.2} />,
    };
  };

  const theme = getTheme();

  return (
    <div className="space-y-4">
      {/* AI Availability Notice (when fallback to rules-only) */}
      {!aiAvailable && (
        <div
          id="ai-unavailable-notice"
          className="flex items-center gap-2 p-3 bg-amber-50/90 border border-amber-200 text-amber-900 text-xs sm:text-sm rounded-xl"
        >
          <Info className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{t.aiUnavailableNotice}</span>
        </div>
      )}

      {/* Main Verdict & Gauge Banner */}
      <div
        id="verdict-banner"
        className={`p-5 sm:p-6 rounded-2xl border ${theme.badgeBg} flex flex-col sm:flex-row items-center justify-between gap-6 transition-all`}
      >
        {/* Left: Verdict info */}
        <div className="flex items-start gap-4 text-center sm:text-left">
          <div className="p-3 bg-white/80 rounded-2xl shadow-xs shrink-0 self-center sm:self-start">
            {theme.icon}
          </div>
          <div>
            <div className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-white/70 border border-slate-200/50 mb-1">
              {t.resultsHeading}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-heading">
              {theme.verdictTitle}
            </h2>
            <p className="text-xs sm:text-sm text-slate-700 mt-1.5 max-w-md leading-relaxed">
              {theme.verdictDesc}
            </p>
          </div>
        </div>

        {/* Right: Circular Gauge */}
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full gauge-svg" viewBox="0 0 100 100">
              {/* Background circle track */}
              <circle
                className="gauge-meter-bg"
                cx="50"
                cy="50"
                r={radius}
                strokeWidth="10"
                fill="transparent"
              />
              {/* Progress animated circle */}
              <circle
                className="gauge-meter-fill"
                cx="50"
                cy="50"
                r={radius}
                strokeWidth="10"
                fill="transparent"
                stroke={theme.stroke}
                strokeDasharray={circumference}
                strokeDashoffset={animatedOffset}
              />
            </svg>

            {/* Inner score label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className={`text-2xl font-black font-heading ${theme.textColor} tracking-tight`}>
                {riskScore}
              </span>
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                / 100
              </span>
            </div>
          </div>
          <span className="text-xs font-bold text-slate-600 mt-1">
            {t.scoreLabel}
          </span>
        </div>
      </div>
    </div>
  );
}
