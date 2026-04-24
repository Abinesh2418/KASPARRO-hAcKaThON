"use client";

import { useRef, useState, useCallback } from "react";
import { Send, ImagePlus, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onSend: (prompt: string) => void;
  onImageUpload: (file: File) => void;
  isStreaming: boolean;
}

export function ChatInput({ onSend, onImageUpload, isStreaming }: Props) {
  const [value, setValue] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleSend = useCallback(() => {
    if (pendingFile) {
      onImageUpload(pendingFile);
      setImagePreview(null);
      setPendingFile(null);
      setValue("");
      return;
    }
    const trimmed = value.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isStreaming, onSend, onImageUpload, pendingFile]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      alert("Image must be under 5 MB");
      return;
    }
    setPendingFile(file);
    const url = URL.createObjectURL(file);
    setImagePreview(url);
    setValue("Search by this image");
  };

  const clearImage = () => {
    setImagePreview(null);
    setPendingFile(null);
    setValue("");
    if (fileRef.current) fileRef.current.value = "";
  };

  const canSend = (value.trim().length > 0 || pendingFile !== null) && !isStreaming;

  return (
    <div className="px-4 pb-4 pt-2">
      <div className="relative flex items-end gap-2 rounded-2xl border border-zinc-700/60 bg-zinc-800/60 px-3 py-2 shadow-xl shadow-black/20 backdrop-blur-sm focus-within:border-violet-500/50 transition-colors">
        {/* Image preview thumbnail */}
        {imagePreview && (
          <div className="relative flex-shrink-0 mb-1">
            <img
              src={imagePreview}
              alt="Upload preview"
              className="h-12 w-12 rounded-lg object-cover border border-zinc-600"
            />
            <button
              onClick={clearImage}
              className="absolute -top-1.5 -right-1.5 h-4 w-4 rounded-full bg-zinc-600 flex items-center justify-center hover:bg-red-500 transition-colors"
            >
              <X className="h-2.5 w-2.5 text-white" />
            </button>
          </div>
        )}

        {/* Photo upload button */}
        <button
          onClick={() => fileRef.current?.click()}
          disabled={isStreaming}
          className={cn(
            "flex-shrink-0 mb-1 p-1.5 rounded-lg text-zinc-400 hover:text-violet-400 hover:bg-zinc-700 transition-colors",
            isStreaming && "opacity-40 cursor-not-allowed"
          )}
          title="Search by image"
        >
          <ImagePlus className="h-5 w-5" />
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
          placeholder={isStreaming ? "Curio is thinking…" : "Ask about a style, occasion, or item…"}
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 outline-none min-h-[36px] max-h-40 py-1.5 leading-relaxed disabled:opacity-60"
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={cn(
            "flex-shrink-0 mb-1 h-8 w-8 rounded-xl flex items-center justify-center transition-all",
            canSend
              ? "bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-900/30"
              : "bg-zinc-700 text-zinc-500 cursor-not-allowed"
          )}
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
      <p className="mt-1.5 text-center text-[10px] text-zinc-600">
        Shift+Enter for new line · Upload a photo to search by style
      </p>
    </div>
  );
}
