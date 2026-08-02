import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { Toaster } from 'sonner';

export const MainLayout: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300">
      {/* Global Toast Provider */}
      <Toaster position="top-right" richColors closeButton />

      {/* Top Navigation */}
      <Navbar
        onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        isMobileMenuOpen={isMobileMenuOpen}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Desktop Collapsible Sidebar */}
        <Sidebar />

        {/* Mobile Navigation Sheet Drawer Overlay */}
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-50 flex md:hidden">
            <div
              className="fixed inset-0 bg-background/80 backdrop-blur-sm"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <div className="relative z-10 w-4/5 max-w-sm bg-card border-r border-border h-full shadow-2xl">
              <Sidebar />
            </div>
          </div>
        )}

        {/* Main Workspace Area */}
        <main className="flex-1 flex flex-col overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl w-full mx-auto flex-1 flex flex-col space-y-6">
            <Breadcrumbs />
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  );
};
