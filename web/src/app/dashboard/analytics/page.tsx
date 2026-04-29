"use client";

import { Star, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { clsx } from "clsx";

const weeklyData = [
  { day: "월", reviews: 12, replies: 12, rating: 4.5 },
  { day: "화", reviews: 18, replies: 17, rating: 4.7 },
  { day: "수", reviews: 8, replies: 8, rating: 4.3 },
  { day: "목", reviews: 22, replies: 21, rating: 4.8 },
  { day: "금", reviews: 15, replies: 15, rating: 4.6 },
  { day: "토", reviews: 9, replies: 9, rating: 4.4 },
  { day: "일", reviews: 6, replies: 6, rating: 4.9 },
];

const topKeywords = [
  { word: "편리한", count: 89, sentiment: "positive" as const },
  { word: "빠른", count: 67, sentiment: "positive" as const },
  { word: "깔끔한", count: 52, sentiment: "positive" as const },
  { word: "업데이트", count: 45, sentiment: "neutral" as const },
  { word: "다크모드", count: 38, sentiment: "neutral" as const },
  { word: "알림", count: 31, sentiment: "neutral" as const },
  { word: "느린", count: 12, sentiment: "negative" as const },
  { word: "오류", count: 8, sentiment: "negative" as const },
];

const sentimentData = {
  positive: 78,
  neutral: 15,
  negative: 7,
};

const platformComparison = [
  {
    platform: "Google Play",
    reviews: 847,
    avgRating: 4.5,
    responseRate: 96,
    change: +0.2,
  },
  {
    platform: "App Store",
    reviews: 400,
    avgRating: 4.7,
    responseRate: 92,
    change: +0.1,
  },
];

const maxReviews = Math.max(...weeklyData.map((d) => d.reviews));

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Period selector */}
      <div className="flex items-center gap-2">
        {["7일", "30일", "90일"].map((period) => (
          <button
            key={period}
            type="button"
            className={clsx(
              "px-4 py-1.5 rounded-lg text-sm font-medium transition",
              period === "7일"
                ? "bg-primary-600 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            )}
          >
            {period}
          </button>
        ))}
      </div>

      {/* Chart + Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-6">일별 리뷰 현황</h2>
          <div className="flex items-end gap-3 h-48">
            {weeklyData.map((d) => (
              <div key={d.day} className="flex-1 flex flex-col items-center">
                <div className="w-full flex flex-col items-center gap-1 flex-1 justify-end">
                  <span className="text-xs text-gray-500 font-medium">
                    {d.reviews}
                  </span>
                  <div
                    className="w-full bg-primary-500 rounded-t-md transition-all"
                    style={{
                      height: `${(d.reviews / maxReviews) * 100}%`,
                      minHeight: "8px",
                    }}
                  />
                </div>
                <span className="text-xs text-gray-400 mt-2">{d.day}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-6 mt-4 pt-4 border-t border-gray-100">
            <div>
              <p className="text-sm text-gray-500">이번 주 총 리뷰</p>
              <p className="text-xl font-bold text-gray-900">
                {weeklyData.reduce((s, d) => s + d.reviews, 0)}건
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">AI 응답률</p>
              <p className="text-xl font-bold text-green-600">98.9%</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">평균 별점</p>
              <p className="text-xl font-bold text-gray-900">4.6</p>
            </div>
          </div>
        </div>

        {/* Sentiment */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-6">감성 분석</h2>
          <div className="space-y-6">
            <SentimentBar
              label="긍정"
              pct={sentimentData.positive}
              color="bg-green-500"
            />
            <SentimentBar
              label="중립"
              pct={sentimentData.neutral}
              color="bg-gray-400"
            />
            <SentimentBar
              label="부정"
              pct={sentimentData.negative}
              color="bg-red-400"
            />
          </div>

          <div className="mt-8 pt-6 border-t border-gray-100">
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              지난주 대비
            </h3>
            <div className="space-y-2">
              <TrendRow label="긍정" value="+3%" trend="up" />
              <TrendRow label="중립" value="-1%" trend="neutral" />
              <TrendRow label="부정" value="-2%" trend="down" />
            </div>
          </div>
        </div>
      </div>

      {/* Keywords + Platform comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Keywords */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">
            자주 언급되는 키워드
          </h2>
          <div className="space-y-3">
            {topKeywords.map((kw) => (
              <div key={kw.word} className="flex items-center gap-3">
                <span
                  className={clsx(
                    "text-xs px-2 py-0.5 rounded font-medium w-16 text-center",
                    kw.sentiment === "positive"
                      ? "bg-green-50 text-green-700"
                      : kw.sentiment === "negative"
                        ? "bg-red-50 text-red-700"
                        : "bg-gray-50 text-gray-600"
                  )}
                >
                  {kw.sentiment === "positive"
                    ? "긍정"
                    : kw.sentiment === "negative"
                      ? "부정"
                      : "중립"}
                </span>
                <span className="text-sm font-medium text-gray-900 w-20">
                  {kw.word}
                </span>
                <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={clsx(
                      "h-full rounded-full",
                      kw.sentiment === "positive"
                        ? "bg-green-400"
                        : kw.sentiment === "negative"
                          ? "bg-red-400"
                          : "bg-gray-400"
                    )}
                    style={{
                      width: `${(kw.count / topKeywords[0].count) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right">
                  {kw.count}회
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Platform comparison */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">플랫폼별 비교</h2>
          <div className="space-y-6">
            {platformComparison.map((p) => (
              <div
                key={p.platform}
                className="border border-gray-100 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <span
                    className={clsx(
                      "text-sm font-medium px-2.5 py-1 rounded",
                      p.platform === "Google Play"
                        ? "bg-green-50 text-green-700"
                        : "bg-blue-50 text-blue-700"
                    )}
                  >
                    {p.platform}
                  </span>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    <span className="text-sm font-bold text-gray-900">
                      {p.avgRating}
                    </span>
                    <span
                      className={`text-xs ${p.change >= 0 ? "text-green-600" : "text-red-500"}`}
                    >
                      {p.change >= 0 ? "+" : ""}
                      {p.change}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">총 리뷰</p>
                    <p className="text-lg font-bold text-gray-900">
                      {p.reviews.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">응답률</p>
                    <p className="text-lg font-bold text-green-600">
                      {p.responseRate}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function SentimentBar({
  label,
  pct,
  color,
}: {
  label: string;
  pct: number;
  color: string;
}) {
  return (
    <div>
      <div className="flex justify-between mb-1.5">
        <span className="text-sm text-gray-600">{label}</span>
        <span className="text-sm font-bold text-gray-900">{pct}%</span>
      </div>
      <div className="bg-gray-100 rounded-full h-3 overflow-hidden">
        <div
          className={`${color} h-full rounded-full transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function TrendRow({
  label,
  value,
  trend,
}: {
  label: string;
  value: string;
  trend: "up" | "down" | "neutral";
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}</span>
      <div className="flex items-center gap-1">
        {trend === "up" ? (
          <TrendingUp className="w-3.5 h-3.5 text-green-500" />
        ) : trend === "down" ? (
          <TrendingDown className="w-3.5 h-3.5 text-green-500" />
        ) : (
          <Minus className="w-3.5 h-3.5 text-gray-400" />
        )}
        <span
          className={clsx(
            "text-sm font-medium",
            trend === "up"
              ? "text-green-600"
              : trend === "down"
                ? "text-green-600"
                : "text-gray-500"
          )}
        >
          {value}
        </span>
      </div>
    </div>
  );
}
