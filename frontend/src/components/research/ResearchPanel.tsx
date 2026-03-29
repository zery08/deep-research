import { useState, useEffect } from "react";
import { useSourceStore } from "../../stores/sourceStore";
import { useResearchStore } from "../../stores/researchStore";
import { researchApi, outlineApi } from "../../api/client";

const STATUS_LABEL: Record<string, string> = {
  pending: "대기 중",
  running: "리서치 진행 중...",
  done: "완료",
  error: "오류 발생",
};

export function ResearchPanel() {
  const [topic, setTopic] = useState("");
  const [isStarting, setIsStarting] = useState(false);
  const { selectedIds } = useSourceStore();
  const { currentJob, setJob, setOutline } = useResearchStore();

  // 잡 상태 폴링
  useEffect(() => {
    if (!currentJob || currentJob.status === "done" || currentJob.status === "error") {
      return;
    }
    const interval = setInterval(async () => {
      const updated = await researchApi.get(currentJob.id);
      setJob(updated);
      if (updated.status === "done" || updated.status === "error") {
        clearInterval(interval);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [currentJob, setJob]);

  // 리서치 완료 시 outline 자동 생성
  useEffect(() => {
    if (currentJob?.status === "done" && !currentJob.outline_id) {
      outlineApi.create(currentJob.id).then((outline) => {
        setOutline(outline);
        // outline 잡 완료까지 폴링은 OutlinePanel에서 처리
      });
    }
  }, [currentJob, setOutline]);

  const handleStart = async () => {
    if (!topic.trim() || selectedIds.size === 0) return;
    setIsStarting(true);
    try {
      const job = await researchApi.create({
        topic: topic.trim(),
        source_ids: Array.from(selectedIds),
      });
      setJob(job);
    } finally {
      setIsStarting(false);
    }
  };

  const isRunning = currentJob?.status === "running" || currentJob?.status === "pending";

  return (
    <div className="p-5 space-y-4">
      <h2 className="text-base font-semibold text-gray-800">딥 리서치</h2>

      {selectedIds.size === 0 && (
        <p className="text-sm text-amber-500 bg-amber-50 rounded-lg px-3 py-2">
          왼쪽에서 소스를 먼저 선택해주세요.
        </p>
      )}

      <div className="space-y-2">
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="발표 주제를 입력하세요&#10;예: AI 기반 신약 개발 동향과 주요 기술"
          rows={3}
          disabled={isRunning}
          className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:bg-gray-50"
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">
            {selectedIds.size}개 소스 선택됨
          </span>
          <button
            onClick={handleStart}
            disabled={!topic.trim() || selectedIds.size === 0 || isRunning}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
          >
            {isStarting ? "시작 중..." : "리서치 시작"}
          </button>
        </div>
      </div>

      {currentJob && (
        <div
          className={`rounded-lg p-4 text-sm space-y-1 ${
            currentJob.status === "error"
              ? "bg-red-50 border border-red-200"
              : currentJob.status === "done"
              ? "bg-green-50 border border-green-200"
              : "bg-blue-50 border border-blue-200"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-medium text-gray-700">{currentJob.topic}</span>
            <span
              className={`text-xs font-semibold ${
                currentJob.status === "error"
                  ? "text-red-500"
                  : currentJob.status === "done"
                  ? "text-green-600"
                  : "text-blue-500"
              }`}
            >
              {STATUS_LABEL[currentJob.status]}
            </span>
          </div>
          {currentJob.status === "running" && (
            <div className="flex items-center gap-2 text-xs text-blue-400">
              <span className="animate-spin">⟳</span>
              <span>에이전트가 소스를 분석하고 있습니다...</span>
            </div>
          )}
          {currentJob.error_message && (
            <p className="text-xs text-red-500">{currentJob.error_message}</p>
          )}
        </div>
      )}
    </div>
  );
}
