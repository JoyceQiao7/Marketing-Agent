/**
 * Main layout component
 */
import { ReactNode } from 'react';
import Link from 'next/link';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
                <span className="text-xl font-bold text-gray-900">
                  Mulan Marketing Agent
                </span>
              </Link>
            </div>
            
            <div className="flex items-center space-x-6">
              <Link
                href="/"
                className="text-gray-700 hover:text-gray-900 font-medium"
              >
                Dashboard
              </Link>
              <Link
                href="/questions"
                className="text-gray-700 hover:text-gray-900 font-medium"
              >
                Questions
              </Link>
              <a
                href={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-700 hover:text-gray-900 font-medium"
              >
                API Docs
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            Mulan Marketing Agent - Automated Social Media Marketing System
          </p>
        </div>
      </footer>
    </div>
  );
}

