import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSourceStore } from "../../stores/sourceStore";
import { sourcesApi } from "../../api/client";
import { SourceUploader } from "./SourceUploader";
import { SourceItem } from "./SourceItem";

export function SourcePanel() {
  const { sources, selectedIds, setSources, selectAll, clearSelection } =
    useSourceStore();

  const { data } = useQuery({
    queryKey: ["sources"],
    queryFn: sourcesApi.list,
    refetchInterval: 5000,
  });

  useEffect(() => {
    if (data) setSources(data);
  }, [data, setSources]);

  const readySources = sources.filter((s) => s.status === "ready");
  const allSelected =
    readySources.length > 0 && readySources.every((s) => selectedIds.has(s.id));

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-100">
        <h2 className="text-base font-semibold text-gray-800 mb-3">소스</h2>
        <SourceUploader />
      </div>

      <div className="flex items-center justify-between px-4 py-2 text-xs text-gray-500 border-b border-gray-100">
        <span>
          {selectedIds.size}/{readySources.length}개 선택됨
        </span>
        <div className="flex gap-2">
          <button
            onClick={allSelected ? clearSelection : selectAll}
            className="hover:text-blue-500 transition-colors"
          >
            {allSelected ? "전체 해제" : "전체 선택"}
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {sources.length === 0 ? (
          <p className="text-sm text-gray-400 text-center mt-8">
            소스를 추가하세요
          </p>
        ) : (
          sources.map((s) => <SourceItem key={s.id} source={s} />)
        )}
      </div>
    </div>
  );
}
