import "./globals.css";
import { Inter } from "next/font/google";


const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});


export const metadata = {
  title: "MxSense Edge AI Console",
  description: "Industrial operations console for edge sensing, AI runtime, quality, and governance.",
};


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
