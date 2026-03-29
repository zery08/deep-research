import { SourcePanel } from "./components/sources/SourcePanel";
import { ResearchPanel } from "./components/research/ResearchPanel";
import { OutlinePanel } from "./components/outline/OutlinePanel";
import { PPTPanel } from "./components/ppt/PPTPanel";

export function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* 좌측: 소스 패널 */}
      <aside className="w-72 min-w-[18rem] border-r border-gray-200 bg-white flex flex-col overflow-hidden">
        <SourcePanel />
      </aside>

      {/* 우측: 메인 영역 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 헤더 */}
        <header className="border-b border-gray-200 bg-white px-6 py-3 flex items-center gap-3">
          <span className="text-lg font-bold text-blue-700">DeepResearch</span>
          <span className="text-gray-300">|</span>
          <span className="text-sm text-gray-500">소스 기반 PPT 자동 생성</span>
        </header>

        {/* 컨텐츠 영역 */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto py-6 space-y-0">
            {/* 리서치 패널 */}
            <section className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <ResearchPanel />
            </section>

            {/* Outline 패널 */}
            <section className="mt-4 bg-white rounded-xl border border-gray-200 overflow-hidden">
              <OutlinePanel />
            </section>

            {/* PPT 상태/다운로드 */}
            <PPTPanel />
          </div>
        </div>
      </main>
    </div>
  );
}
