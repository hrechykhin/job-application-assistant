import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { LoadingSpinner } from './LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders md size by default', () => {
    const { container } = render(<LoadingSpinner />)
    expect(container.querySelector('.h-8.w-8')).toBeTruthy()
  })

  it('renders sm size', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    expect(container.querySelector('.h-4.w-4')).toBeTruthy()
  })

  it('renders lg size', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    expect(container.querySelector('.h-12.w-12')).toBeTruthy()
  })
})
