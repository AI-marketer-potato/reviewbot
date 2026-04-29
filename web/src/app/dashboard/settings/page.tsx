"use client";

import { useState } from "react";
import {
  Key,
  Globe,
  Bot,
  Bell,
  Shield,
  Save,
  Eye,
  EyeOff,
} from "lucide-react";
import { clsx } from "clsx";

export default function SettingsPage() {
  const [autoReply, setAutoReply] = useState(false);
  const [slackNotify, setSlackNotify] = useState(true);
  const [emailNotify, setEmailNotify] = useState(true);
  const [negativeAlert, setNegativeAlert] = useState(true);
  const [showApiKey, setShowApiKey] = useState(false);

  return (
    <div className="max-w-3xl space-y-8">
      {/* Store connections */}
      <section className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Globe className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">스토어 연동</h2>
            <p className="text-sm text-gray-500">
              앱 스토어 API 키를 등록하세요
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Google Play */}
          <div className="border border-gray-100 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium bg-green-50 text-green-700 px-2 py-0.5 rounded">
                  Google Play
                </span>
                <span className="text-xs text-green-600 font-medium">
                  연동됨
                </span>
              </div>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  Service Account JSON
                </label>
                <input
                  type="text"
                  value="service_account_******.json"
                  readOnly
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 text-gray-600"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  패키지명
                </label>
                <input
                  type="text"
                  defaultValue="com.example.myapp"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>

          {/* App Store */}
          <div className="border border-gray-100 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                  App Store
                </span>
                <span className="text-xs text-green-600 font-medium">
                  연동됨
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  Key ID
                </label>
                <input
                  type="text"
                  defaultValue="DJ9W6DK66M"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  Issuer ID
                </label>
                <input
                  type="text"
                  defaultValue="********-****-****"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="col-span-2">
                <label className="text-xs text-gray-500 block mb-1">
                  Bundle ID
                </label>
                <input
                  type="text"
                  defaultValue="com.example.myapp"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Response settings */}
      <section className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">AI 응답 설정</h2>
            <p className="text-sm text-gray-500">
              응답 스타일과 자동화 수준을 설정하세요
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              응답 톤
            </label>
            <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option>친근하고 따뜻한 톤</option>
              <option>전문적이고 격식있는 톤</option>
              <option>캐주얼한 톤</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              응답 대상 별점
            </label>
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <label
                  key={star}
                  className="flex items-center gap-1.5 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    defaultChecked={star >= 3}
                    className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-600">{star}점</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between py-3 border-t border-gray-100">
            <div>
              <p className="text-sm font-medium text-gray-700">
                완전 자동 응답
              </p>
              <p className="text-xs text-gray-500">
                승인 없이 바로 게시합니다 (4~5점 리뷰만)
              </p>
            </div>
            <Toggle checked={autoReply} onChange={setAutoReply} />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              커스텀 지시사항
            </label>
            <textarea
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              placeholder="예: 항상 '내친소 팀'으로 서명해주세요. 이모지를 적절히 사용해주세요."
              defaultValue="항상 따뜻한 인사로 시작하고, 구체적인 피드백에는 개선 계획을 언급해주세요."
            />
          </div>
        </div>
      </section>

      {/* Notifications */}
      <section className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Bell className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">알림 설정</h2>
            <p className="text-sm text-gray-500">
              알림을 받을 채널을 선택하세요
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-medium text-gray-700">이메일 알림</p>
              <p className="text-xs text-gray-500">
                일간 리뷰 요약을 이메일로 받습니다
              </p>
            </div>
            <Toggle checked={emailNotify} onChange={setEmailNotify} />
          </div>
          <div className="flex items-center justify-between py-2 border-t border-gray-100">
            <div>
              <p className="text-sm font-medium text-gray-700">Slack 알림</p>
              <p className="text-xs text-gray-500">
                새 리뷰가 등록되면 Slack 채널에 알림
              </p>
            </div>
            <Toggle checked={slackNotify} onChange={setSlackNotify} />
          </div>
          <div className="flex items-center justify-between py-2 border-t border-gray-100">
            <div>
              <p className="text-sm font-medium text-gray-700">부정 리뷰 긴급 알림</p>
              <p className="text-xs text-gray-500">
                1~2점 리뷰가 등록되면 즉시 알림
              </p>
            </div>
            <Toggle checked={negativeAlert} onChange={setNegativeAlert} />
          </div>
        </div>
      </section>

      {/* API Key */}
      <section className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Key className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">API 키</h2>
            <p className="text-sm text-gray-500">
              외부 시스템과 연동할 때 사용합니다
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            type={showApiKey ? "text" : "password"}
            value="rm_live_a1b2c3d4e5f6g7h8i9j0"
            readOnly
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 font-mono"
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="p-2 text-gray-400 hover:text-gray-600 transition"
          >
            {showApiKey ? (
              <EyeOff className="w-5 h-5" />
            ) : (
              <Eye className="w-5 h-5" />
            )}
          </button>
        </div>
      </section>

      {/* Save */}
      <div className="flex justify-end">
        <button
          type="button"
          className="flex items-center gap-2 bg-primary-600 text-white px-6 py-2.5 rounded-xl hover:bg-primary-700 transition font-medium"
        >
          <Save className="w-4 h-4" />
          저장하기
        </button>
      </div>
    </div>
  );
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={clsx(
        "relative w-11 h-6 rounded-full transition-colors",
        checked ? "bg-primary-600" : "bg-gray-200"
      )}
    >
      <span
        className={clsx(
          "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow",
          checked && "translate-x-5"
        )}
      />
    </button>
  );
}
