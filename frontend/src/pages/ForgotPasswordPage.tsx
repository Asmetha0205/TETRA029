import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';
import { toast } from 'sonner';

export const ForgotPasswordPage: React.FC = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Password reset link sent to your email.');
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-foreground tracking-tight">Reset Password</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Enter your academic email address and we'll send you a password reset link.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="email"
                placeholder="professor@university.edu"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full h-10 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow-md hover:opacity-90 transition-opacity"
          >
            Send Reset Instructions
          </button>
        </form>

        <div className="text-center text-xs text-muted-foreground">
          <Link to="/login" className="inline-flex items-center gap-1 text-primary hover:underline">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Sign In
          </Link>
        </div>
      </div>
    </PageTransition>
  );
};
