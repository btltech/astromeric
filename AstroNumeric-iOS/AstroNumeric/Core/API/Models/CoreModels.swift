// CoreModels.swift
// Shared base types used across all domains

import Foundation

// MARK: - V2 API Response Wrapper

/// Generic wrapper for v2 API responses that return {status: string, data: T}
struct V2ApiResponse<T: Decodable>: Decodable {
    let status: String
    let data: T
}

extension V2ApiResponse: Encodable where T: Encodable {}
