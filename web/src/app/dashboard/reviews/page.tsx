"use client";

import { useState } from "react";
import {
  Star,
  Bot,
  Search,
  Filter,
  ChevronDown,
  Check,
  X,
  Edit3,
  RotateCcw,
} from "lucide-react";
import { clsx } from "clsx";

type ReviewStatus = "all" | "pending" | "replied" | "edited";
type Platform = "all" | "google_play" | "app_store";

interface Review {
  id: number;
  author: string;
  rating: number;
  text: string;
  platform: "Google Play" | "App Store";
  time: string;
  status: "pending" | "replied" | "edited";
  aiReply: string;
}

const mockReviews: Review[] = [
  {
    id: 1,
    author: "김*준",
    rating: 5,
    text: "매일 쓰는 앱이에요. 업데이트도 자주 해주시고 감사합니다!",
    platform: "Google Play",
    time: "10분 전",
    status: "pending",
    aiReply:
      "소중한 리뷰 감사합니다! 앞으로도 더 좋은 서비스를 제공할 수 있도록 노력하겠습니다.",
  },
  {
    id: 2,
    author: "이*영",
    rating: 4,
    text: "전반적으로 좋은데, 다크모드 지원이 있으면 좋겠어요.",
    platform: "App Store",
    time: "25분 전",
    status: "pending",
    aiReply:
      "좋은 의견 감사합니다! 다크모드는 다음 업데이트에서 지원할 예정입니다. 기대해주세요!",
  },
  {
    id: 3,
    author: "박*수",
    rating: 5,
    text: "깔끔한 UI, 빠른 속도. 완벽합니다.",
    platform: "Google Play",
    time: "1시간 전",
    status: "replied",
    aiReply:
      "최고의 칭찬 감사드립니다! 앞으로도 깔끔하고 빠른 서비스를 유지하겠습니다.",
  },
  {
    id: 4,
    author: "최*은",
    rating: 4,
    text: "유용한 앱이에요. 위젯 기능이 추가되면 더 좋을 것 같아요.",
    platform: "App Store",
    time: "2시간 전",
    status: "edited",
    aiReply:
      "리뷰 감사합니다! 위젯 기능은 현재 개발 검토 중입니다. 좋은 제안 감사해요!",
  },
  {
    id: 5,
    author: "정*호",
    rating: 5,
    text: "오프라인에서도 쓸 수 있어서 너무 좋아요. 강추합니다.",
    platform: "Google Play",
    time: "3시간 전",
    status: "replied",
    aiReply:
      "오프라인 기능을 잘 활용해주시다니 감사합니다! 앞으로도 편리한 기능을 계속 추가하겠습니다.",
  },
  {
    id: 6,
    author: "한*지",
    rating: 3,
    text: "기능은 좋은데, 가끔 앱이 느려지는 느낌이 있어요.",
    platform: "App Store",
    time: "4시간 전",
    status: "pending",
    aiReply:
      "이용에 불편을 드려 죄송합니다. 성능 개선에 집중하고 있으며, 다음 업데이트에서 개선될 예정입니다.",
  },
  {
    id: 7,
    author: "윤*민",
    rating: 5,
    text: "디자인이 정말 예쁘고 직관적이에요. 다른 앱들도 이렇게 만들어주세요.",
    platform: "Google Play",
    time: "5시간 전",
    status: "replied",
    aiReply:
      "디자인을 좋아해주셔서 감사합니다! 더 좋은 사용자 경험을 위해 끊임없이 개선하겠습니다.",
  },
  {
    id: 8,
    author: "서*아",
    rating: 4,
    text: "알림 기능이 유용해요. 시간대별로 설정할 수 있으면 더 좋겠습니다.",
    platform: "App Store",
    time: "6시간 전",
    status: "pending",
    aiReply:
      "유용하게 사용해주셔서 감사합니다! 시간대별 알림 설정은 좋은 아이디어네요. 검토해보겠습니다!",
  },
];

const statusLabels: Record<ReviewStatus, string> = {
  all: "전체",
  pending: "승인 대기",
  replied: "응답 완료",
  edited: "수정 완료",
};

export default function ReviewsPage() {
  const [statusFilter, setStatusFilter] = useState<ReviewStatus>("all");
  const [platformFilter, setPlatformFilter] = useState<Platform>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = mockReviews.filter((r) => {
    if (statusFilter !== "all" && r.status !== statusFilter) return false;
    if (
      platformFilter === "google_play" &&
      r.platform !== "Google Play"
    )
      return false;
    if (platformFilter === "app_store" && r.platform !== "App Store")
      return false;
    if (
      searchQuery &&
      !r.text.includes(searchQuery) &&
      !r.author.includes(searchQuery)
    )
      return false;
    return true;
  });

  const pendingCount = mockReviews.filter(
    (r) => r.status === "pending"
  ).length;

  return (
    <div className="space-y-6">
      {/* Header + filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <p className="text-sm text-gray-500">
            총 {mockReviews.length}건 · 승인 대기{" "}
            <span className="text-primary-600 font-medium">
              {pendingCount}건
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="리뷰 검색..."
              className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-60"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <select
            className="border border-gray-200 rounded-lg text-sm px-3 py-2 text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value as Platform)}
          >
            <option value="all">전체 플랫폼</option>
            <option value="google_play">Google Play</option>
            <option value="app_store">App Store</option>
          </select>
        </div>
      </div>

      {/* Status tabs */}
      <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg w-fit">
        {(Object.entries(statusLabels) as [ReviewStatus, string][]).map(
          ([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => setStatusFilter(key)}
              className={clsx(
                "px-4 py-1.5 rounded-md text-sm font-medium transition",
                statusFilter === key
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              )}
            >
              {label}
              {key === "pending" && pendingCount > 0 && (
                <span className="ml-1.5 bg-primary-100 text-primary-700 text-xs px-1.5 py-0.5 rounded-full">
                  {pendingCount}
                </span>
              )}
            </button>
          )
        )}
      </div>

      {/* Review list */}
      <div className="space-y-3">
        {filtered.map((review) => (
          <div
            key={review.id}
            className="bg-white rounded-xl border border-gray-200 p-5 hover:border-gray-300 transition"
          >
            {/* Review header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className={`w-4 h-4 ${
                        i < review.rating
                          ? "text-yellow-400 fill-yellow-400"
                          : "text-gray-200"
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm font-medium text-gray-900">
                  {review.author}
                </span>
                <span
                  className={clsx(
                    "text-xs px-2 py-0.5 rounded font-medium",
                    review.platform === "Google Play"
                      ? "bg-green-50 text-green-700"
                      : "bg-blue-50 text-blue-700"
                  )}
                >
                  {review.platform}
                </span>
                <span
                  className={clsx(
                    "text-xs px-2 py-0.5 rounded font-medium",
                    review.status === "pending"
                      ? "bg-amber-50 text-amber-700"
                      : review.status === "replied"
                        ? "bg-green-50 text-green-700"
                        : "bg-purple-50 text-purple-700"
                  )}
                >
                  {review.status === "pending"
                    ? "대기"
                    : review.status === "replied"
                      ? "완료"
                      : "수정됨"}
                </span>
              </div>
              <span className="text-xs text-gray-400">{review.time}</span>
            </div>

            {/* Review text */}
            <p className="text-sm text-gray-700 mb-4">{review.text}</p>

            {/* AI Reply */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <Bot className="w-4 h-4 text-primary-600" />
                  <span className="text-xs font-medium text-primary-700">
                    AI 생성 응답
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {review.status === "pending" && (
                    <>
                      <button
                        type="button"
                        className="flex items-center gap-1 text-xs bg-primary-600 text-white px-3 py-1.5 rounded-md hover:bg-primary-700 transition"
                      >
                        <Check className="w-3 h-3" />
                        승인
                      </button>
                      <button
                        type="button"
                        className="flex items-center gap-1 text-xs text-gray-500 px-3 py-1.5 rounded-md hover:bg-gray-100 transition"
                      >
                        <Edit3 className="w-3 h-3" />
                        수정
                      </button>
                      <button
                        type="button"
                        className="flex items-center gap-1 text-xs text-gray-500 px-3 py-1.5 rounded-md hover:bg-gray-100 transition"
                      >
                        <RotateCcw className="w-3 h-3" />
                        재생성
                      </button>
                    </>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-600">{review.aiReply}</p>
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <MessageSquareEmpty className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>조건에 맞는 리뷰가 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function MessageSquareEmpty({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"
      />
    </svg>
  );
}
