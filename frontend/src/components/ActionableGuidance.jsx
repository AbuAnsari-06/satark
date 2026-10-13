import React, { useState } from "react";
import {
  ListChecks,
  PhoneCall,
  ExternalLink,
  Check,
  Users,
  FileText,
} from "lucide-react";
import { translations } from "../i18n";

export default function ActionableGuidance({
  nextSteps = [],
  familyAlert,
  reportSummary,
  verdict,
  lang,
}) {
  const t = translations[lang] || translations.en;
  const isSafe = verdict === "Safe";

  const [copiedType, setCopiedType] = useState(null); // 'family' | 'report' | null

  const handleCopy = async (type, textToCopy) => {
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopiedType(type);
      setTimeout(() => setCopiedType(null), 2500);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = textToCopy;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopiedType(type);
      setTimeout(() => setCopiedType(null), 2500);
    }
  };

  const getFamilyAlertText = () => {
    if (!familyAlert) return "";
    if (typeof familyAlert === "string") return familyAlert;
    return lang === "hi" && familyAlert.hi ? familyAlert.hi : familyAlert.en || "";
  };

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-6 border border-slate-200 space-y-6 relative">
      {/* Toast Notification */}
      {copiedType && (
        <div
          id="copied-toast"
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-xs sm:text-sm font-semibold shadow-xl border border-slate-700 animate-bounce"
        >
          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{t.copiedToast}</span>
        </div>
      )}

      {/* Section 1: Recommended Next Steps Checklist */}
      <div>
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm sm:text-base font-heading mb-4">
          <ListChecks className="w-5 h-5 text-blue-600" />
          <span>{t.nextStepsHeading}</span>
        </div>

        <ul className="space-y-3">
          {nextSteps.map((step, idx) => (
            <li
              key={idx}
              className={`p-3.5 rounded-xl border flex items-start gap-3 transition-colors ${
                isSafe
                  ? "bg-emerald-50/50 border-emerald-200/80 text-emerald-950"
                  : "bg-slate-50 border-slate-200 text-slate-800"
              }`}
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs ${
                  isSafe
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-blue-100 text-blue-800"
                }`}
              >
                {idx + 1}
              </div>
              <div className="text-xs sm:text-sm leading-relaxed font-medium">
                {step}
              </div>
            </li>
          ))}
        </ul>

        {/* Official Indian Cyber Crime Helpline & Portal Highlights */}
        {!isSafe && (
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {/* National 1930 Helpline */}
            <a
              id="helpline-1930-cta"
              href="tel:1930"
              className="flex items-center justify-between p-3.5 rounded-xl bg-rose-50 hover:bg-rose-100/80 border border-rose-200 text-rose-900 transition-all group"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-rose-200/80 flex items-center justify-center text-rose-700">
                  <PhoneCall className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-rose-700">
                    {t.helplineTitle}
                  </div>
                  <div className="text-sm font-extrabold text-rose-900">
                    Dial 1930
                  </div>
                </div>
              </div>
              <span className="text-xs font-semibold underline text-rose-700 group-hover:text-rose-900">
                Call Now
              </span>
            </a>

            {/* National Cybercrime Portal */}
            <a
              id="cybercrime-portal-cta"
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-3.5 rounded-xl bg-blue-50 hover:bg-blue-100/80 border border-blue-200 text-blue-900 transition-all group"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-200/80 flex items-center justify-center text-blue-700">
                  <ExternalLink className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-blue-700">
                    Official Portal
                  </div>
                  <div className="text-sm font-extrabold text-blue-900 truncate max-w-[140px] sm:max-w-none">
                    cybercrime.gov.in
                  </div>
                </div>
              </div>
              <span className="text-xs font-semibold underline text-blue-700 group-hover:text-blue-900">
                Report Incident
              </span>
            </a>
          </div>
        )}
      </div>

      {/* Section 2: Copyable Sharing Tools (Task 4.5.2) */}
      <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row gap-3">
        {/* Copy Family Alert Button */}
        <button
          id="copy-family-alert-btn"
          type="button"
          onClick={() => handleCopy("family", getFamilyAlertText())}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-xs sm:text-sm bg-slate-900 hover:bg-slate-800 text-white transition-all cursor-pointer shadow-sm active:scale-98"
        >
          {copiedType === "family" ? (
            <Check className="w-4 h-4 text-emerald-400" />
          ) : (
            <Users className="w-4 h-4 text-blue-300" />
          )}
          <span>{t.familyAlertBtn}</span>
        </button>

        {/* Copy Report Summary Button */}
        <button
          id="copy-report-summary-btn"
          type="button"
          onClick={() => handleCopy("report", reportSummary)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-xs sm:text-sm bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 transition-all cursor-pointer shadow-2xs active:scale-98"
        >
          {copiedType === "report" ? (
            <Check className="w-4 h-4 text-emerald-600" />
          ) : (
            <FileText className="w-4 h-4 text-slate-600" />
          )}
          <span>{t.reportSummaryBtn}</span>
        </button>
      </div>
    </div>
  );
}
