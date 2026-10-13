import React, { useRef, useState } from "react";
import { UploadCloud, X, FileText, AlertCircle, ShieldCheck, Loader2 } from "lucide-react";
import { translations } from "../i18n";

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
const ALLOWED_MIME_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp"];

export default function InputCard({
  text,
  setText,
  imageFile,
  setImageFile,
  imagePreview,
  setImagePreview,
  onAnalyze,
  isLoading,
  lang,
  children,
}) {
  const t = translations[lang] || translations.en;
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileError, setFileError] = useState("");

  const handleFileSelection = (file) => {
    setFileError("");
    if (!file) return;

    if (!ALLOWED_MIME_TYPES.includes(file.type.toLowerCase())) {
      setFileError(
        lang === "hi"
          ? "केवल PNG, JPG या WebP छवियाँ स्वीकार्य हैं।"
          : "Invalid file type. Only PNG, JPG, JPEG, and WebP are supported."
      );
      return;
    }

    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      setFileError(
        lang === "hi"
          ? "छवि का आकार 5 MB से कम होना चाहिए।"
          : "File size exceeds the 5 MB limit. Please choose a smaller image."
      );
      return;
    }

    setImageFile(file);
    const objectUrl = URL.createObjectURL(file);
    setImagePreview(objectUrl);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const removeImage = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setImageFile(null);
    setImagePreview(null);
    setFileError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="glass-card-elevated rounded-2xl p-5 sm:p-7 transition-all">
      <div className="mb-5">
        <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight font-heading flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          {t.inputHeading}
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 mt-1">
          {t.inputSubheading}
        </p>
      </div>

      {/* Main Textarea Input */}
      <div className="relative mb-5">
        <textarea
          id="message-input-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t.textareaPlaceholder}
          rows={4}
          className="w-full rounded-xl border border-slate-300 bg-slate-50/60 hover:bg-slate-50 focus:bg-white px-4 py-3 text-sm sm:text-base text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:ring-3 focus:ring-blue-100 transition-all resize-y custom-scrollbar font-sans"
        />
        <div className="flex items-center justify-between mt-1.5 px-1 text-xs text-slate-400">
          <span>
            {text.length > 0 && (
              <button
                type="button"
                onClick={() => setText("")}
                className="text-slate-500 hover:text-slate-800 underline cursor-pointer"
              >
                {lang === "hi" ? "साफ़ करें" : "Clear text"}
              </button>
            )}
          </span>
          <span>
            {text.length} {t.charCount}
          </span>
        </div>
      </div>

      {/* Screenshot Upload Dropzone / Preview */}
      <div className="mb-5">
        {!imagePreview ? (
          <div
            id="screenshot-dropzone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
              isDragging
                ? "border-blue-500 bg-blue-50/70 scale-[0.99]"
                : "border-slate-300 bg-slate-50/40 hover:bg-slate-100/70 hover:border-slate-400"
            }`}
          >
            <input
              id="screenshot-file-input"
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileSelection(e.target.files[0]);
                }
              }}
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-1.5 pointer-events-none">
              <div className="w-10 h-10 rounded-full bg-blue-100/80 flex items-center justify-center text-blue-600 mb-1">
                <UploadCloud className="w-5 h-5" />
              </div>
              <p className="text-xs sm:text-sm font-semibold text-slate-700">
                {t.dropzoneTitle}{" "}
                <span className="text-blue-600 hover:underline">{t.dropzoneBrowse}</span>
              </p>
              <p className="text-[11px] sm:text-xs text-slate-400">
                {t.dropzoneSub}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between p-3.5 bg-blue-50/60 border border-blue-200 rounded-xl gap-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-12 h-12 rounded-lg overflow-hidden border border-slate-200 bg-white shrink-0 relative flex items-center justify-center">
                <img
                  src={imagePreview}
                  alt="Screenshot preview"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="truncate">
                <p className="text-xs sm:text-sm font-semibold text-slate-900 truncate">
                  {imageFile?.name || "screenshot.png"}
                </p>
                <p className="text-[11px] text-slate-500">
                  {imageFile ? formatFileSize(imageFile.size) : ""} • Ready for scan
                </p>
              </div>
            </div>
            <button
              id="remove-screenshot-btn"
              type="button"
              onClick={removeImage}
              className="p-1.5 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-200 transition-colors cursor-pointer shrink-0"
              title={t.removeImage}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* File Error Notice */}
        {fileError && (
          <div className="flex items-center gap-2 mt-2 text-xs text-red-600 bg-red-50 p-2.5 rounded-lg border border-red-200">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{fileError}</span>
          </div>
        )}
        {/* Primary Action Button */}
        <div className="mt-5 mb-5">
          <button
            id="analyze-submit-btn"
            type="button"
            onClick={onAnalyze}
            disabled={(!text.trim() && !imageFile) || isLoading}
            className={`w-full py-3.5 px-6 rounded-xl font-bold text-sm sm:text-base flex items-center justify-center gap-2.5 shadow-md transition-all cursor-pointer ${
              (!text.trim() && !imageFile) || isLoading
                ? "bg-slate-200 text-slate-400 cursor-not-allowed shadow-none"
                : "bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-700 hover:to-indigo-700 text-white shadow-blue-500/25 active:scale-[0.99] hover:shadow-lg"
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>{t.analyzingBtn}</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-5 h-5" />
                <span>{t.analyzeBtn}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Children slot for Sample Chips */}
      {children}
    </div>
  );
}
