import React from "react";
import { Link2, AlertTriangle } from "lucide-react";
import { translations } from "../i18n";

export default function LinkInspector({ links = [], lang }) {
  const t = translations[lang] || translations.en;

  // Completely hidden if no links detected
  if (!links || links.length === 0) {
    return null;
  }

  const getRiskBadge = (risk) => {
    switch (risk?.toLowerCase()) {
      case "high":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-rose-100 text-rose-800 border border-rose-300">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-pulse" />
            {lang === "hi" ? "उच्च (High)" : "High"}
          </span>
        );
      case "medium":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-300">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
            {lang === "hi" ? "मध्यम (Med)" : "Medium"}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 border border-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
            {lang === "hi" ? "कम (Low)" : "Low"}
          </span>
        );
    }
  };

  return (
    <div id="link-inspector-card" className="glass-card rounded-2xl p-5 sm:p-6 border border-slate-200">
      <div className="flex items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm sm:text-base font-heading">
          <Link2 className="w-4 h-4 text-blue-600" />
          <span>{t.linkInspectorHeading}</span>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
          {links.length} {links.length === 1 ? "URL" : "URLs"}
        </span>
      </div>

      {/* Table container with horizontal scroll for small viewports (360px) */}
      <div className="overflow-x-auto custom-scrollbar -mx-2 sm:mx-0">
        <div className="inline-block min-w-full align-middle px-2 sm:px-0">
          <table className="min-w-full divide-y divide-slate-200 border border-slate-200/90 rounded-xl overflow-hidden text-left">
            <thead className="bg-slate-100/80 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th scope="col" className="px-3.5 py-2.5">{t.linkTableUrl}</th>
                <th scope="col" className="px-3 py-2.5">{t.linkTableShortener}</th>
                <th scope="col" className="px-3 py-2.5">{t.linkTableTld}</th>
                <th scope="col" className="px-3.5 py-2.5">{t.linkTableLookalike}</th>
                <th scope="col" className="px-3.5 py-2.5 text-right">{t.linkTableRisk}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white text-xs sm:text-sm">
              {links.map((link, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                  {/* Domain / URL */}
                  <td className="px-3.5 py-3 font-medium text-slate-900 max-w-[180px] sm:max-w-xs">
                    <div className="font-semibold text-slate-800 break-all">{link.domain}</div>
                    <div className="text-[11px] text-slate-400 truncate mt-0.5" title={link.url}>
                      {link.url}
                    </div>
                  </td>

                  {/* Shortener */}
                  <td className="px-3 py-3 text-slate-700 whitespace-nowrap">
                    {link.is_shortener ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                        {t.yes}
                      </span>
                    ) : (
                      <span className="text-slate-400 text-xs">{t.no}</span>
                    )}
                  </td>

                  {/* Suspicious TLD */}
                  <td className="px-3 py-3 text-slate-700 whitespace-nowrap">
                    {link.suspicious_tld ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-rose-50 text-rose-800 border border-rose-200">
                        {t.yes}
                      </span>
                    ) : (
                      <span className="text-slate-400 text-xs">{t.no}</span>
                    )}
                  </td>

                  {/* Lookalike brand */}
                  <td className="px-3.5 py-3 whitespace-nowrap">
                    {link.lookalike_of ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-rose-100 text-rose-900 border border-rose-300">
                        <AlertTriangle className="w-3 h-3 text-rose-600 shrink-0" />
                        {lang === "hi" ? `नकली ${link.lookalike_of}` : `Spoofs ${link.lookalike_of}`}
                      </span>
                    ) : (
                      <span className="text-slate-400 text-xs">{t.none}</span>
                    )}
                  </td>

                  {/* Risk Tier */}
                  <td className="px-3.5 py-3 text-right whitespace-nowrap">
                    {getRiskBadge(link.risk)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
