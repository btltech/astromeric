// RetryPolicy.swift
// Exponential backoff retry configuration

import Foundation

struct RetryPolicy {
    let maxAttempts: Int
    let initialDelay: TimeInterval
    let maxDelay: TimeInterval
    let retryableStatusCodes: Set<Int>
    
    static let `default` = RetryPolicy(
        maxAttempts: 3,
        initialDelay: 0.5,
        maxDelay: 8.0,
        retryableStatusCodes: [408, 429, 500, 502, 503, 504]
    )
    
    static let aggressive = RetryPolicy(
        maxAttempts: 5,
        initialDelay: 0.25,
        maxDelay: 16.0,
        retryableStatusCodes: [408, 429, 500, 502, 503, 504]
    )
    
    static let none = RetryPolicy(
        maxAttempts: 1,
        initialDelay: 0,
        maxDelay: 0,
        retryableStatusCodes: []
    )
    
    /// Calculate delay for a given attempt with exponential backoff + jitter
    func delay(for attempt: Int) -> TimeInterval {
        let exponentialDelay = initialDelay * pow(2.0, Double(attempt - 1))
        let jitter = Double.random(in: 0...0.3) * exponentialDelay
        return min(exponentialDelay + jitter, maxDelay)
    }
}
