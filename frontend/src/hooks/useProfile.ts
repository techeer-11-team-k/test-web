/**
 * 프로필 조회 및 수정 훅
 * 
 * 백엔드 API를 사용하여 사용자 프로필을 조회하고 수정합니다.
 */
import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/clerk';
import apiClient, { ApiResponse } from '@/lib/api';

interface Profile {
  account_id: number;
  clerk_user_id: string;
  email: string;
  nickname: string;
  profile_image_url: string | null;
  last_login_at: string | null;
  created_at: string;
}

interface UpdateProfileData {
  nickname?: string;
  profile_image_url?: string;
}

export function useProfile() {
  const { isSignedIn, getToken } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 프로필 조회
   */
  const fetchProfile = async () => {
    if (!isSignedIn) {
      setProfile(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<ApiResponse<Profile>>('/auth/me');
      setProfile(response.data.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail?.message || '프로필을 불러오는데 실패했습니다.';
      setError(errorMessage);
      console.error('프로필 조회 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 프로필 수정
   */
  const updateProfile = async (data: UpdateProfileData) => {
    if (!isSignedIn) {
      throw new Error('로그인이 필요합니다.');
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.patch<ApiResponse<Profile>>('/auth/me', data);
      setProfile(response.data.data);
      return response.data.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail?.message || '프로필 수정에 실패했습니다.';
      setError(errorMessage);
      console.error('프로필 수정 실패:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 로그인 상태가 변경되면 프로필 조회
  useEffect(() => {
    if (isSignedIn) {
      fetchProfile();
    } else {
      setProfile(null);
    }
  }, [isSignedIn]);

  return {
    profile,
    loading,
    error,
    fetchProfile,
    updateProfile,
  };
}
