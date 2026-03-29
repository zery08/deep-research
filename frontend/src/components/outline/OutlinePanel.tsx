import { useState, useEffect } from "react";
import { useResearchStore } from "../../stores/researchStore";
import { outlineApi, pptApi } from "../../api/client";
import type { Slide } from "../../types";

export function OutlinePanel() {
  const { currentOutline, currentJob, setOutline, setPPT } = useResearchStore();
  const [isGenerating, setIsGenerating] = useState(false);

  // outline 생성 완료까지 폴링
  useEffect(() => {
    if (!currentOutline || currentOutline.slides.length > 0) return;
    const interval = setInterval(async () => {
      const updated = await outlineApi.get(currentOutline.id);
      setOutline(updated);
      if (updated.slides.length > 0) clearInterval(interval);
    }, 2000);
    return () => clearInterval(interval);
  }, [currentOutline, setOutline]);

  const handleGeneratePPT = async () => {
    if (!currentOutline) return;
    setIsGenerating(true);
    try {
      const pptJob = await pptApi.generate(currentOutline.id);
      setPPT(pptJob);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!currentJob || currentJob.status !== "done") {
    return (
      <div className="p-5 text-sm text-gray-400">
        리서치가 완료되면 슬라이드 outline이 여기에 표시됩니다.
      </div>
    );
  }

  if (!currentOutline) {
    return (
      <div className="p-5 text-sm text-blue-500">
        <span className="animate-spin inline-block mr-2">⟳</span>
        Outline 생성 중...
      </div>
    );
  }

  if (currentOutline.slides.length === 0) {
    return (
      <div className="p-5 text-sm text-blue-500">
        <span className="animate-spin inline-block mr-2">⟳</span>
        슬라이드 구성 중...
      </div>
    );
  }

  return (
    <div className="p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-800">슬라이드 Outline</h2>
        <button
          onClick={handleGeneratePPT}
          disabled={isGenerating}
          className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-40 transition-colors"
        >
          {isGenerating ? "생성 중..." : "PPT 생성"}
        </button>
      </div>

      <h3 className="text-sm font-semibold text-gray-600">{currentOutline.title}</h3>

      <div className="space-y-2">
        {currentOutline.slides.map((slide) => (
          <SlideCard key={slide.index} slide={slide} />
        ))}
      </div>
    </div>
  );
}

function SlideCard({ slide }: { slide: Slide }) {
  const TYPE_COLOR: Record<Slide["type"], string> = {
    title: "bg-blue-100 text-blue-700",
    section: "bg-purple-100 text-purple-700",
    content: "bg-gray-100 text-gray-600",
    closing: "bg-green-100 text-green-700",
    references: "bg-orange-100 text-orange-700",
  };

  const TYPE_LABEL: Record<Slide["type"], string> = {
    title: "타이틀",
    section: "섹션",
    content: "내용",
    closing: "결론",
    references: "참고",
  };

  return (
    <div className="border border-gray-200 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-400 font-mono w-5">{slide.index}</span>
        <span
          className={`text-xs px-1.5 py-0.5 rounded font-medium ${TYPE_COLOR[slide.type]}`}
        >
          {TYPE_LABEL[slide.type]}
        </span>
        <span className="text-sm font-medium text-gray-800">{slide.title}</span>
      </div>
      {slide.bullets.length > 0 && (
        <ul className="ml-7 space-y-0.5">
          {slide.bullets.map((b, i) => (
            <li key={i} className="text-xs text-gray-500">
              • {b}
            </li>
          ))}
        </ul>
      )}
      {slide.sources.length > 0 && (
        <div className="ml-7 flex flex-wrap gap-1">
          {slide.sources.map((s, i) => (
            <span
              key={i}
              className="text-xs bg-yellow-50 text-yellow-700 px-1.5 py-0.5 rounded border border-yellow-200"
              title={s.text}
            >
              {s.source_name}
              {s.page ? ` p.${s.page}` : ""}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
