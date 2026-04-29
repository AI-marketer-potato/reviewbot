import Link from "next/link";
import {
  Bot,
  Star,
  Zap,
  Shield,
  BarChart3,
  MessageSquareReply,
  Clock,
  Globe,
  ChevronRight,
  Check,
  ArrowRight,
} from "lucide-react";

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg text-gray-900">리뷰메이트</span>
        </Link>
        <div className="hidden md:flex items-center gap-8 text-sm text-gray-600">
          <a href="#features" className="hover:text-gray-900 transition">
            기능
          </a>
          <a href="#how-it-works" className="hover:text-gray-900 transition">
            작동방식
          </a>
          <a href="#pricing" className="hover:text-gray-900 transition">
            요금제
          </a>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="text-sm text-gray-600 hover:text-gray-900 transition"
          >
            로그인
          </Link>
          <Link
            href="/dashboard"
            className="text-sm bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition font-medium"
          >
            무료로 시작하기
          </Link>
        </div>
      </div>
    </nav>
  );
}

function StatCard({
  label,
  value,
  trend,
}: {
  label: string;
  value: string;
  trend: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-gray-900">{value}</span>
        <span className="text-xs text-green-600 font-medium mb-1">
          {trend}
        </span>
      </div>
    </div>
  );
}

function Hero() {
  return (
    <section className="pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 bg-primary-50 text-primary-700 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <Zap className="w-4 h-4" />
          한국 앱 개발자를 위한 AI 리뷰 응답
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight mb-6">
          앱 리뷰 응답,
          <br />
          <span className="text-primary-600">AI가 대신합니다</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          Google Play와 App Store의 리뷰를 자동으로 분석하고, 브랜드 톤에 맞는
          응답을 생성합니다. 더 이상 리뷰 하나하나에 시간 쓰지 마세요.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 bg-primary-600 text-white px-8 py-3.5 rounded-xl hover:bg-primary-700 transition font-semibold text-lg shadow-lg shadow-primary-600/25"
          >
            무료로 시작하기
            <ArrowRight className="w-5 h-5" />
          </Link>
          <a
            href="#how-it-works"
            className="flex items-center gap-2 text-gray-600 px-8 py-3.5 rounded-xl hover:bg-gray-50 transition font-medium"
          >
            어떻게 작동하나요?
            <ChevronRight className="w-4 h-4" />
          </a>
        </div>
        <p className="text-sm text-gray-400 mt-4">
          신용카드 없이 시작 · 매월 50건 무료
        </p>
      </div>

      {/* Hero mockup */}
      <div className="max-w-5xl mx-auto mt-16">
        <div className="bg-gray-900 rounded-2xl shadow-2xl p-1 ring-1 ring-white/10">
          <div className="flex items-center gap-2 px-4 py-3">
            <div className="w-3 h-3 rounded-full bg-red-400" />
            <div className="w-3 h-3 rounded-full bg-yellow-400" />
            <div className="w-3 h-3 rounded-full bg-green-400" />
            <span className="text-gray-500 text-xs ml-2">
              리뷰메이트 대시보드
            </span>
          </div>
          <div className="bg-gray-50 rounded-xl p-6 m-1">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <StatCard label="오늘 응답한 리뷰" value="23" trend="+12%" />
              <StatCard label="평균 응답 시간" value="< 1분" trend="-85%" />
              <StatCard label="평균 별점" value="4.6" trend="+0.3" />
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-start gap-3 mb-3">
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star
                      key={i}
                      className="w-4 h-4 text-yellow-400 fill-yellow-400"
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-500">Google Play</span>
              </div>
              <p className="text-sm text-gray-700 mb-3">
                &quot;정말 편리한 앱이에요! 매일 사용하고 있습니다. 다만 알림
                설정이 좀 더 세분화되면 좋겠어요.&quot;
              </p>
              <div className="bg-primary-50 rounded-lg p-3 border border-primary-100">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Bot className="w-3.5 h-3.5 text-primary-600" />
                  <span className="text-xs font-medium text-primary-700">
                    AI 생성 응답
                  </span>
                </div>
                <p className="text-sm text-gray-700">
                  &quot;소중한 리뷰 감사합니다! 매일 사용해주신다니 정말
                  기쁩니다. 알림 설정 세분화는 다음 업데이트에서 개선할
                  예정이에요. 더 나은 경험을 위해 노력하겠습니다!&quot;
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Features() {
  const features = [
    {
      icon: MessageSquareReply,
      title: "AI 자동 응답",
      desc: "리뷰 내용을 분석해 브랜드 톤에 맞는 자연스러운 응답을 자동 생성합니다.",
    },
    {
      icon: Clock,
      title: "실시간 모니터링",
      desc: "새 리뷰가 등록되면 즉시 감지하고, 설정에 따라 자동 또는 승인 후 응답합니다.",
    },
    {
      icon: BarChart3,
      title: "리뷰 분석 대시보드",
      desc: "별점 추이, 감성 분석, 키워드 트렌드를 한눈에 파악할 수 있습니다.",
    },
    {
      icon: Globe,
      title: "Google Play & App Store",
      desc: "두 스토어의 리뷰를 하나의 대시보드에서 통합 관리합니다.",
    },
    {
      icon: Shield,
      title: "승인 모드",
      desc: "AI가 생성한 응답을 게시 전에 검토하고 수정할 수 있습니다. 완전 자동화도 가능합니다.",
    },
    {
      icon: Zap,
      title: "한국어 특화",
      desc: "한국어 리뷰에 최적화된 AI 모델로, 자연스러운 존댓말과 이모지 사용을 지원합니다.",
    },
  ];

  return (
    <section id="features" className="py-20 px-6 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            리뷰 관리, 이렇게 쉬워집니다
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">
            리뷰 하나에 5분씩 쓰던 시간, AI가 5초로 줄여드립니다.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-white rounded-xl p-6 border border-gray-200 hover:border-primary-200 hover:shadow-lg transition-all group"
            >
              <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-100 transition">
                <f.icon className="w-5 h-5 text-primary-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      num: "01",
      title: "스토어 연동",
      desc: "Google Play Console과 App Store Connect API 키를 등록하면 자동으로 리뷰를 수집합니다.",
    },
    {
      num: "02",
      title: "AI가 응답 생성",
      desc: "리뷰 내용, 별점, 맥락을 분석해 브랜드에 맞는 응답을 자동으로 작성합니다.",
    },
    {
      num: "03",
      title: "검토 후 게시",
      desc: "승인 모드에서 AI 응답을 확인하고 수정한 뒤 게시하거나, 완전 자동으로 운영할 수 있습니다.",
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            3단계로 시작하세요
          </h2>
          <p className="text-gray-500 text-lg">
            복잡한 설정 없이 5분 안에 시작할 수 있습니다.
          </p>
        </div>
        <div className="space-y-8">
          {steps.map((s, i) => (
            <div key={s.num} className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-14 h-14 bg-primary-600 rounded-2xl flex items-center justify-center text-white font-bold text-lg">
                {s.num}
              </div>
              <div className="pt-2">
                <h3 className="font-semibold text-lg text-gray-900 mb-1">
                  {s.title}
                </h3>
                <p className="text-gray-500 leading-relaxed">{s.desc}</p>
                {i < steps.length - 1 && (
                  <div className="w-px h-8 bg-gray-200 ml-0 mt-4" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    {
      name: "무료",
      price: "0",
      period: "원/월",
      desc: "개인 개발자를 위한 시작 플랜",
      features: [
        "월 50건 AI 응답",
        "Google Play 1개 앱",
        "기본 감성 분석",
        "이메일 알림",
      ],
      cta: "무료로 시작",
      highlight: false,
    },
    {
      name: "프로",
      price: "29,000",
      period: "원/월",
      desc: "성장하는 앱을 위한 플랜",
      features: [
        "월 500건 AI 응답",
        "Google Play + App Store",
        "앱 3개까지",
        "고급 분석 대시보드",
        "Slack 알림 연동",
        "승인 모드",
      ],
      cta: "프로 시작하기",
      highlight: true,
    },
    {
      name: "팀",
      price: "79,000",
      period: "원/월",
      desc: "여러 앱을 운영하는 팀",
      features: [
        "무제한 AI 응답",
        "앱 무제한",
        "팀 멤버 5명",
        "커스텀 응답 톤 설정",
        "API 접근",
        "우선 지원",
      ],
      cta: "팀 시작하기",
      highlight: false,
    },
  ];

  return (
    <section id="pricing" className="py-20 px-6 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            심플한 요금제
          </h2>
          <p className="text-gray-500 text-lg">
            필요한 만큼만 쓰세요. 언제든 업그레이드 가능합니다.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-8 ${
                plan.highlight
                  ? "bg-primary-600 text-white ring-4 ring-primary-600/20 scale-105"
                  : "bg-white border border-gray-200"
              }`}
            >
              <h3
                className={`font-semibold text-lg mb-1 ${plan.highlight ? "text-white" : "text-gray-900"}`}
              >
                {plan.name}
              </h3>
              <p
                className={`text-sm mb-6 ${plan.highlight ? "text-primary-100" : "text-gray-500"}`}
              >
                {plan.desc}
              </p>
              <div className="flex items-baseline gap-1 mb-6">
                <span
                  className={`text-4xl font-bold ${plan.highlight ? "text-white" : "text-gray-900"}`}
                >
                  {plan.price}
                </span>
                <span
                  className={`text-sm ${plan.highlight ? "text-primary-200" : "text-gray-400"}`}
                >
                  {plan.period}
                </span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <Check
                      className={`w-4 h-4 flex-shrink-0 ${plan.highlight ? "text-primary-200" : "text-primary-500"}`}
                    />
                    <span
                      className={
                        plan.highlight ? "text-primary-50" : "text-gray-600"
                      }
                    >
                      {f}
                    </span>
                  </li>
                ))}
              </ul>
              <Link
                href="/dashboard"
                className={`block text-center py-3 rounded-xl font-medium transition ${
                  plan.highlight
                    ? "bg-white text-primary-600 hover:bg-primary-50"
                    : "bg-primary-600 text-white hover:bg-primary-700"
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-gray-100">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-primary-600 rounded-md flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-gray-900">리뷰메이트</span>
        </div>
        <p className="text-sm text-gray-400">
          &copy; 2026 ReviewMate. All rights reserved.
        </p>
      </div>
    </footer>
  );
}

export default function LandingPage() {
  return (
    <>
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Pricing />
      <Footer />
    </>
  );
}
