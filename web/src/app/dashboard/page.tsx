"use client";

import {
  MessageSquare,
  TrendingUp,
  Clock,
  Star,
  Bot,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";

const stats = [
  {
    label: "총 리뷰",
    value: "1,247",
    change: "+38",
    trend: "up" as const,
    period: "이번 주",
    icon: MessageSquare,
  },
  {
    label: "AI 응답 완료",
    value: "1,183",
    change: "94.8%",
    trend: "up" as const,
    period: "응답률",
    icon: Bot,
  },
  {
    label: "평균 응답 시간",
    value: "47초",
    change: "-23초",
    trend: "up" as const,
    period: "지난주 대비",
    icon: Clock,
  },
  {
    label: "평균 별점",
    value: "4.6",
    change: "+0.2",
    trend: "up" as const,
    period: "지난달 대비",
    icon: Star,
  },
];

const recentReviews = [
  {
    id: 1,
    author: "김*준",
    rating: 5,
    text: "매일 쓰는 앱이에요. 업데이트도 자주 해주시고 감사합니다!",
    platform: "Google Play",
    time: "10분 전",
    status: "replied" as const,
    reply:
      "소중한 리뷰 감사합니다! 앞으로도 더 좋은 서비스를 제공할 수 있도록 노력하겠습니다.",
  },
  {
    id: 2,
    author: "이*영",
    rating: 4,
    text: "전반적으로 좋은데, 다크모드 지원이 있으면 좋겠어요.",
    platform: "App Store",
    time: "25분 전",
    status: "pending" as const,
    reply:
      "좋은 의견 감사합니다! 다크모드는 다음 업데이트에서 지원할 예정입니다. 기대해주세요!",
  },
  {
    id: 3,
    author: "박*수",
    rating: 5,
    text: "깔끔한 UI, 빠른 속도. 완벽합니다.",
    platform: "Google Play",
    time: "1시간 전",
    status: "replied" as const,
    reply:
      "최고의 칭찬 감사드립니다! 앞으로도 깔끔하고 빠른 서비스를 유지하겠습니다.",
  },
  {
    id: 4,
    author: "최*은",
    rating: 4,
    text: "유용한 앱이에요. 위젯 기능이 추가되면 더 좋을 것 같아요.",
    platform: "App Store",
    time: "2시간 전",
    status: "pending" as const,
    reply:
      "리뷰 감사합니다! 위젯 기능은 현재 개발 검토 중입니다. 좋은 제안 감사해요!",
  },
];

const ratingDistribution = [
  { stars: 5, count: 823, pct: 66 },
  { stars: 4, count: 287, pct: 23 },
  { stars: 3, count: 89, pct: 7 },
  { stars: 2, count: 31, pct: 3 },
  { stars: 1, count: 17, pct: 1 },
];

export default function DashboardOverview() {
  return (
    <div className="space-y-8">
      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-xl border border-gray-200 p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                <s.icon className="w-5 h-5 text-primary-600" />
              </div>
              <div
                className={`flex items-center gap-1 text-xs font-medium ${
                  s.trend === "up" ? "text-green-600" : "text-red-500"
                }`}
              >
                {s.trend === "up" ? (
                  <ArrowUpRight className="w-3.5 h-3.5" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5" />
                )}
                {s.change}
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-900">{s.value}</p>
            <p className="text-xs text-gray-500 mt-1">
              {s.label} · {s.period}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent reviews */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center justify-between p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">최근 리뷰</h2>
            <span className="text-xs text-gray-500">
              {recentReviews.filter((r) => r.status === "pending").length}건
              승인 대기
            </span>
          </div>
          <div className="divide-y divide-gray-100">
            {recentReviews.map((review) => (
              <div key={review.id} className="p-5">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${
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
                    <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded">
                      {review.platform}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">{review.time}</span>
                </div>
                <p className="text-sm text-gray-700 mb-3">{review.text}</p>

                {/* AI Reply */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <Bot className="w-3.5 h-3.5 text-primary-600" />
                      <span className="text-xs font-medium text-primary-700">
                        AI 응답
                      </span>
                    </div>
                    {review.status === "pending" ? (
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          className="text-xs bg-primary-600 text-white px-3 py-1 rounded-md hover:bg-primary-700 transition"
                        >
                          승인
                        </button>
                        <button
                          type="button"
                          className="text-xs text-gray-500 px-3 py-1 rounded-md hover:bg-gray-100 transition"
                        >
                          수정
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-green-600 font-medium">
                        게시됨
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{review.reply}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Rating distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">별점 분포</h2>
          <div className="text-center mb-6">
            <div className="text-5xl font-bold text-gray-900">4.6</div>
            <div className="flex items-center justify-center gap-0.5 mt-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 ${
                    i < 5
                      ? "text-yellow-400 fill-yellow-400"
                      : "text-gray-200"
                  }`}
                />
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-1">1,247개 리뷰</p>
          </div>
          <div className="space-y-3">
            {ratingDistribution.map((r) => (
              <div key={r.stars} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-6">{r.stars}</span>
                <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-yellow-400 h-full rounded-full transition-all"
                    style={{ width: `${r.pct}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right">
                  {r.count}
                </span>
              </div>
            ))}
          </div>

          {/* Quick stats */}
          <div className="mt-8 pt-6 border-t border-gray-100 space-y-4">
            <h3 className="font-medium text-gray-900 text-sm">이번 주 요약</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">새 리뷰</span>
                <span className="font-medium text-gray-900">38건</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">자동 응답</span>
                <span className="font-medium text-gray-900">34건</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">수동 수정</span>
                <span className="font-medium text-gray-900">4건</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">긍정 리뷰 비율</span>
                <span className="font-medium text-green-600">89%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
