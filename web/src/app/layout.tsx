import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FeedbackForm", description: "From scattered thoughts to shared direction.",
  icons: { icon: "/lightbulb.svg" },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
