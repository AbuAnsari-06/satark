import React from "react";
import { MessageSquare, AlertCircle } from "lucide-react";
import { translations } from "../i18n";

/**
 * Escapes regex special characters in substring.
 */
function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export default function HighlightedMessage({
  text,
  suspiciousPhrases = [],
  verdict,
  lang,
}) {
  const t = translations[lang] || translations.en;

  // Filter valid phrases
  const validPhrases = (suspiciousPhrases || [])
    .map((p) => (typeof p === "string" ? p.trim() : ""))
    .filter((p) => p.length > 0);

  // Render highlighted elements safely using React elements (no dangerouslySetInnerHTML)
  const renderContent = () => {
    if (!text) return null;
    if (validPhrases.length === 0 || verdict === "Safe") {
      return <span>{text}</span>;
    }

    try {
      // Sort phrases descending by length so longer substrings match first
      const sorted = [...validPhrases].sort((a, b) => b.length - a.length);
      const pattern = `(${sorted.map(escapeRegex).join("|")})`;
      const regex = new RegExp(pattern, "gi");

      const parts = text.split(regex);
      const lowerPhrases = new Set(sorted.map((p) => p.toLowerCase()));

      return parts.map((part, index) => {
        if (!part) return null;

        const isMatch = lowerPhrases.has(part.toLowerCase());

        if (isMatch) {
          const highlightClass =
            verdict === "Likely Scam" ? "highlight-danger" : "highlight-warning";

          return (
            <mark
              key={`match-${index}`}
              className={highlightClass}
              title={lang === "hi" ? "संदेहास्पद शब्द" : "Flagged suspicious phrase"}
            >
              {part}
            </mark>
          );
        }

        return <React.Fragment key={`text-${index}`}>{part}</React.Fragment>;
      });
    } catch {
      // Fail-safe: Render unmodified text if regex evaluation fails
      return <span>{text}</span>;
    }
  };

  const hasHighlights = validPhrases.length > 0 && verdict !== "Safe";

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-6 border border-slate-200">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm sm:text-base font-heading">
          <MessageSquare className="w-4 h-4 text-blue-600" />
          <span>{t.messageHeading}</span>
        </div>

        {hasHighlights && (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
            <AlertCircle className="w-3 h-3 text-amber-600" />
            <span className="hidden xs:inline">{t.highlightHint}</span>
            <span className="xs:hidden">{validPhrases.length} flags</span>
          </span>
        )}
      </div>

      <div
        id="analyzed-message-view"
        className="p-4 rounded-xl bg-slate-50/80 border border-slate-200/90 text-slate-800 text-sm sm:text-base leading-relaxed font-sans whitespace-pre-wrap break-words custom-scrollbar max-h-60 overflow-y-auto"
      >
        {renderContent()}
      </div>
    </div>
  );
}
