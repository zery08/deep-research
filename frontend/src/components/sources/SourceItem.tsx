import { useSourceStore } from "../../stores/sourceStore";
import { sourcesApi } from "../../api/client";
import type { Source } from "../../types";

const STATUS_LABEL: Record<Source["status"], string> = {
  pending: "대기 중",
  indexing: "인덱싱 중...",
  ready: "준비됨",
  error: "오류",
};

const STATUS_COLOR: Record<Source["status"], string> = {
  pending: "text-gray-400",
  indexing: "text-blue-500",
  ready: "text-green-500",
  error: "text-red-500",
};

const TYPE_ICON: Record<Source["type"], string> = {
  pdf: "📄",
  pptx: "📊",
  url: "🔗",
};

interface Props {
  source: Source;
}

export function SourceItem({ source }: Props) {
  const { selectedIds, toggleSelected, removeSource } = useSourceStore();
  const isSelected = selectedIds.has(source.id);
  const isReady = source.status === "ready";

  const handleDelete = async () => {
    await sourcesApi.delete(source.id);
    removeSource(source.id);
  };

  return (
    <div
      className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
        isSelected
          ? "border-blue-500 bg-blue-50"
          : "border-gray-200 bg-white hover:border-gray-300"
      }`}
    >
      <input
        type="checkbox"
        checked={isSelected}
        disabled={!isReady}
        onChange={() => toggleSelected(source.id)}
        className="w-4 h-4 accent-blue-500 disabled:opacity-40 cursor-pointer"
      />

      <span className="text-lg">{TYPE_ICON[source.type]}</span>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">{source.name}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className={`text-xs font-medium ${STATUS_COLOR[source.status]}`}>
            {STATUS_LABEL[source.status]}
          </span>
          {isReady && (
            <span className="text-xs text-gray-400">{source.chunk_count}개 청크</span>
          )}
          {source.error_message && (
            <span className="text-xs text-red-400 truncate">{source.error_message}</span>
          )}
        </div>
      </div>

      <button
        onClick={handleDelete}
        className="text-gray-300 hover:text-red-400 transition-colors text-xs px-1"
        title="삭제"
      >
        ✕
      </button>
    </div>
  );
}
