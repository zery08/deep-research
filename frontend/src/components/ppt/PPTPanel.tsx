import { useEffect } from "react";
import { useResearchStore } from "../../stores/researchStore";
import { pptApi } from "../../api/client";

const STATUS_LABEL: Record<string, string> = {
  pending: "대기 중",
  generating: "PPT 생성 중...",
  done: "생성 완료",
  error: "오류 발생",
};

export function PPTPanel() {
  const { currentPPT, setPPT } = useResearchStore();

  useEffect(() => {
    if (!currentPPT || currentPPT.status === "done" || currentPPT.status === "error") {
      return;
    }
    const interval = setInterval(async () => {
      const updated = await pptApi.get(currentPPT.id);
      setPPT(updated);
      if (updated.status === "done" || updated.status === "error") {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [currentPPT, setPPT]);

  if (!currentPPT) return null;

  return (
    <div
      className={`mx-5 mb-5 rounded-lg p-4 text-sm ${
        currentPPT.status === "done"
          ? "bg-green-50 border border-green-200"
          : currentPPT.status === "error"
          ? "bg-red-50 border border-red-200"
          : "bg-blue-50 border border-blue-200"
      }`}
    >
      <div className="flex items-center justify-between">
        <span
          className={`font-medium ${
            currentPPT.status === "done"
              ? "text-green-700"
              : currentPPT.status === "error"
              ? "text-red-600"
              : "text-blue-600"
          }`}
        >
          {currentPPT.status === "generating" && (
            <span className="animate-spin inline-block mr-2">⟳</span>
          )}
          {STATUS_LABEL[currentPPT.status]}
        </span>

        {currentPPT.status === "done" && (
          <a
            href={pptApi.downloadUrl(currentPPT.id)}
            download
            className="px-4 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition-colors"
          >
            다운로드 (.pptx)
          </a>
        )}
      </div>

      {currentPPT.error_message && (
        <p className="mt-1 text-xs text-red-500">{currentPPT.error_message}</p>
      )}
    </div>
  );
}
