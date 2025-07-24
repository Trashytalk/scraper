import { describe, it, expect } from 'vitest'

describe('Basic Test Setup', () => {
  it('should pass a basic test', () => {
    expect(true).toBe(true)
  })

  it('should handle basic arithmetic', () => {
    expect(2 + 2).toBe(4)
  })

  it('should handle string operations', () => {
    expect('hello' + ' world').toBe('hello world')
  })
})
