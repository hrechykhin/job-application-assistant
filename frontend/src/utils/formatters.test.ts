import { describe, it, expect } from 'vitest'
import { formatDate, formatPercent, STATUS_LABELS, STATUS_COLORS } from './formatters'

const ALL_STATUSES = ['SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED']

describe('formatDate', () => {
  it('formats an ISO datetime string', () => {
    expect(formatDate('2024-03-15T10:00:00.000Z')).toBe('15 Mar 2024')
  })

  it('formats a date-only string', () => {
    expect(formatDate('2024-01-01')).toMatch(/1 Jan 2024/)
  })
})

describe('formatPercent', () => {
  it('converts 0.5 to 50%', () => {
    expect(formatPercent(0.5)).toBe('50%')
  })

  it('rounds down', () => {
    expect(formatPercent(0.333)).toBe('33%')
  })

  it('handles 0', () => {
    expect(formatPercent(0)).toBe('0%')
  })

  it('handles 1', () => {
    expect(formatPercent(1)).toBe('100%')
  })
})

describe('STATUS_LABELS', () => {
  it('has a label for every status', () => {
    ALL_STATUSES.forEach((s) => {
      expect(STATUS_LABELS).toHaveProperty(s)
      expect(typeof STATUS_LABELS[s]).toBe('string')
    })
  })
})

describe('STATUS_COLORS', () => {
  it('has a Tailwind class string for every status', () => {
    ALL_STATUSES.forEach((s) => {
      expect(STATUS_COLORS).toHaveProperty(s)
      expect(typeof STATUS_COLORS[s]).toBe('string')
    })
  })
})
