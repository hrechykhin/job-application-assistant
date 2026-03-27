import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { authApi } from '../api/auth'

type State = 'loading' | 'success' | 'error'

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [state, setState] = useState<State>('loading')

  useEffect(() => {
    if (!token) {
      setState('error')
      return
    }
    authApi
      .verifyEmail(token)
      .then(() => setState('success'))
      .catch(() => setState('error'))
  }, [token])

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-slate-200 bg-white px-8 py-10 shadow-sm text-center space-y-3">
          {state === 'loading' && (
            <>
              <div className="flex justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
              </div>
              <p className="text-sm text-slate-500">Verifying your email…</p>
            </>
          )}

          {state === 'success' && (
            <>
              <div className="text-4xl">✓</div>
              <h1 className="text-2xl font-bold text-slate-900">Email verified!</h1>
              <p className="text-sm text-slate-500">Your account is now active. You can sign in.</p>
              <Link
                to="/login"
                className="mt-2 inline-block rounded-lg bg-brand-600 px-5 py-2 text-sm font-medium text-white hover:bg-brand-700 transition-colors"
              >
                Sign in
              </Link>
            </>
          )}

          {state === 'error' && (
            <>
              <div className="text-4xl">✕</div>
              <h1 className="text-2xl font-bold text-slate-900">Link expired or invalid</h1>
              <p className="text-sm text-slate-500">
                This verification link is no longer valid. Please register again to get a new link.
              </p>
              <Link
                to="/register"
                className="mt-2 inline-block text-sm text-brand-600 hover:underline"
              >
                Back to sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
