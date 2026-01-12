/**
 * 인증 버튼 컴포넌트
 * 
 * Clerk를 사용하여 로그인/로그아웃 기능을 제공합니다.
 */
import { useUser, useAuth, SignInButton, SignOutButton, SignUpButton } from '@/lib/clerk';
import { LogIn, User } from 'lucide-react';

interface AuthButtonProps {
  className?: string;
}

export default function AuthButton({ className = '' }: AuthButtonProps) {
  // Clerk가 설정되지 않은 경우를 대비한 안전장치
  let isSignedIn = false;
  let user = null;
  let signOut: (() => Promise<void>) | null = null;
  
  try {
    const userData = useUser();
    const authData = useAuth();
    isSignedIn = userData.isSignedIn || false;
    user = userData.user || null;
    signOut = authData.signOut || null;
  } catch (error) {
    // Clerk Provider가 없거나 설정되지 않은 경우
    console.warn('Clerk가 설정되지 않았습니다:', error);
  }

  if (isSignedIn && user) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="flex items-center gap-2 px-3 py-2 bg-zinc-100 dark:bg-zinc-900 rounded-xl">
          {user.imageUrl ? (
            <img
              src={user.imageUrl}
              alt={user.firstName || 'User'}
              className="w-6 h-6 rounded-full"
            />
          ) : (
            <div className="w-6 h-6 rounded-full bg-sky-500 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
          <span className="text-sm font-medium text-zinc-900 dark:text-white">
            {user.firstName || user.emailAddresses[0]?.emailAddress || 'User'}
          </span>
        </div>
        <SignOutButton>
          <button className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-medium transition-colors">
            로그아웃
          </button>
        </SignOutButton>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <SignInButton mode="modal">
        <button className="flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white rounded-xl text-sm font-medium transition-colors">
          <LogIn className="w-4 h-4" />
          로그인
        </button>
      </SignInButton>
      <SignUpButton mode="modal">
        <button className="px-4 py-2 bg-zinc-200 dark:bg-zinc-800 hover:bg-zinc-300 dark:hover:bg-zinc-700 text-zinc-900 dark:text-white rounded-xl text-sm font-medium transition-colors">
          회원가입
        </button>
      </SignUpButton>
    </div>
  );
}
