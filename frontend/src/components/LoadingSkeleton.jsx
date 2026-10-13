import React from "react";
import { Loader2 } from "lucide-react";
import { translations } from "../i18n";

export default function LoadingSkeleton({ lang }) {
  const t = translations[lang] || translations.en;

  return (
    <div
      id="analysis-loading-skeleton"
      className="glass-card-elevated rounded-2xl p-6 sm:p-8 mt-6 border border-slate-200/90 shadow-lg animate-pulse"
    >
      {/* Skeleton Header banner */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl skeleton-shimmer shrink-0" />
          <div className="space-y-2">
            <div className="h-6 w-36 sm:w-48 skeleton-shimmer rounded-md" />
            <div className="h-4 w-48 sm:w-64 skeleton-shimmer rounded-md" />
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          <span>{t.analyzingBtn}</span>
        </div>
      </div>

      {/* Grid: Circular Gauge placeholder + Message View placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-6 border-b border-slate-100">
        {/* Gauge placeholder */}
        <div className="md:col-span-1 flex flex-col items-center justify-center p-4">
          <div className="w-32 h-32 rounded-full skeleton-shimmer" />
          <div className="h-4 w-24 skeleton-shimmer rounded-md mt-3" />
        </div>

        {/* Message placeholder */}
        <div className="md:col-span-2 space-y-3 justify-center flex flex-col">
          <div className="h-4 w-32 skeleton-shimmer rounded-md" />
          <div className="h-16 w-full skeleton-shimmer rounded-xl" />
          <div className="flex gap-2">
            <div className="h-6 w-20 skeleton-shimmer rounded-full" />
            <div className="h-6 w-28 skeleton-shimmer rounded-full" />
            <div className="h-6 w-24 skeleton-shimmer rounded-full" />
          </div>
        </div>
      </div>

      {/* Score breakdown + Explanation placeholders */}
      <div className="py-6 space-y-4">
        <div className="h-4 w-44 skeleton-shimmer rounded-md" />
        <div className="h-5 w-full skeleton-shimmer rounded-lg" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
          <div className="h-20 skeleton-shimmer rounded-xl" />
          <div className="h-20 skeleton-shimmer rounded-xl" />
        </div>
      </div>

      {/* Next steps placeholder */}
      <div className="pt-4 flex flex-wrap gap-3">
        <div className="h-10 w-36 skeleton-shimmer rounded-xl" />
        <div className="h-10 w-44 skeleton-shimmer rounded-xl" />
      </div>
    </div>
  );
}
