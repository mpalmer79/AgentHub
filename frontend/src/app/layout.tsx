import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AgentHub - AI Agents for SMB Operations',
  description:
    'Deploy AI agents to automate your business operations. Bookkeeping, email, hiring, support, and more.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-white text-slate-900`}>
        {children}
      </body>
    </html>
  )
}
