import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'

vi.mock('../api/auth', () => ({
  authApi: {
    me: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
    verifyEmail: vi.fn(),
  },
}))

import { authApi } from '../api/auth'

const mockApi = authApi as {
  me: ReturnType<typeof vi.fn>
  login: ReturnType<typeof vi.fn>
  register: ReturnType<typeof vi.fn>
  verifyEmail: ReturnType<typeof vi.fn>
}

const MOCK_USER = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
}

const MOCK_TOKENS = {
  access_token: 'access-abc',
  refresh_token: 'refresh-xyz',
  token_type: 'bearer',
}

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('throws when used outside AuthProvider', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => renderHook(() => useAuth())).toThrow('useAuth must be used inside AuthProvider')
    spy.mockRestore()
  })

  it('starts unauthenticated when no token is stored', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.user).toBeNull()
    expect(mockApi.me).not.toHaveBeenCalled()
  })

  it('loads the user from a stored token on mount', async () => {
    localStorage.setItem('access_token', 'existing-token')
    mockApi.me.mockResolvedValueOnce(MOCK_USER)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.user).toEqual(MOCK_USER)
    expect(mockApi.me).toHaveBeenCalledOnce()
  })

  it('clears storage when the stored token is invalid', async () => {
    localStorage.setItem('access_token', 'bad-token')
    mockApi.me.mockRejectedValueOnce(new Error('Unauthorized'))

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('login stores tokens and sets the user', async () => {
    mockApi.login.mockResolvedValueOnce(MOCK_TOKENS)
    mockApi.me.mockResolvedValueOnce(MOCK_USER)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(async () => {
      await result.current.login('test@example.com', 'password123')
    })

    expect(localStorage.getItem('access_token')).toBe('access-abc')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-xyz')
    expect(result.current.user).toEqual(MOCK_USER)
  })

  it('logout clears storage and removes the user', async () => {
    localStorage.setItem('access_token', 'token')
    mockApi.me.mockResolvedValueOnce(MOCK_USER)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.user).toEqual(MOCK_USER))

    act(() => result.current.logout())

    expect(result.current.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('register calls the register API and does not log in automatically', async () => {
    mockApi.register.mockResolvedValueOnce(MOCK_USER)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(async () => {
      await result.current.register('test@example.com', 'password123', 'Test User')
    })

    expect(mockApi.register).toHaveBeenCalledWith('test@example.com', 'password123', 'Test User')
    expect(mockApi.login).not.toHaveBeenCalled()
    expect(result.current.user).toBeNull()
  })
})
