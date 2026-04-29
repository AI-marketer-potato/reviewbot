import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "리뷰메이트 - AI 앱 리뷰 자동응답",
  description:
    "Google Play & App Store 리뷰에 AI가 자동으로 응답합니다. 한국 앱 개발자를 위한 리뷰 관리 서비스.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full antialiased scroll-smooth">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
        />
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
