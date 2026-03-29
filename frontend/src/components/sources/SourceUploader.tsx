import { useRef, useState } from "react";
import { useSourceStore } from "../../stores/sourceStore";
import { sourcesApi } from "../../api/client";

export function SourceUploader() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState("");
  const [urlName, setUrlName] = useState("");
  const [isAddingUrl, setIsAddingUrl] = useState(false);
  const [uploading, setUploading] = useState(false);
  const { sources, updateSource, setSources } = useSourceStore();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (!files.length) return;

    setUploading(true);
    try {
      for (const file of files) {
        const source = await sourcesApi.upload(file);
        setSources([source, ...sources]);
        // 인덱싱 완료까지 폴링
        pollStatus(source.id);
      }
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleAddUrl = async () => {
    if (!url.trim()) return;
    setIsAddingUrl(true);
    try {
      const source = await sourcesApi.addUrl(url.trim(), urlName.trim() || undefined);
      setSources([source, ...sources]);
      pollStatus(source.id);
      setUrl("");
      setUrlName("");
    } finally {
      setIsAddingUrl(false);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      const updated = await sourcesApi.get(id);
      updateSource(updated);
      if (updated.status === "ready" || updated.status === "error") {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div className="space-y-3">
      {/* 파일 업로드 */}
      <button
        onClick={() => fileRef.current?.click()}
        disabled={uploading}
        className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-blue-400 hover:text-blue-500 transition-colors disabled:opacity-50"
      >
        {uploading ? "업로드 중..." : "+ PDF / PPT 파일 추가"}
      </button>
      <input
        ref={fileRef}
        type="file"
        accept=".pdf,.ppt,.pptx"
        multiple
        className="hidden"
        onChange={handleFileChange}
      />

      {/* URL 추가 */}
      <div className="space-y-2">
        <input
          type="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAddUrl()}
          className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="표시 이름 (선택)"
            value={urlName}
            onChange={(e) => setUrlName(e.target.value)}
            className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <button
            onClick={handleAddUrl}
            disabled={!url.trim() || isAddingUrl}
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-40 transition-colors"
          >
            {isAddingUrl ? "추가 중..." : "추가"}
          </button>
        </div>
      </div>
    </div>
  );
}
