// APIClient.swift
// Resilient URLSession-based HTTP client with retry and caching

import Foundation

actor APIClient {
    static let shared = APIClient()
    
    private var baseURL: URL
    private var isBaseURLResolved = false
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let cache = ResponseCache.shared
    private let retryPolicy = RetryPolicy.default
    private let session: URLSession
    
    init() {
        // Important: Avoid Info.plist reads here to prevent slow-launch warnings.
        // We resolve API_BASE_URL lazily on first network request from a non-main actor executor.
        self.baseURL = URL(string: "https://astromeric-backend-production.up.railway.app")!
        
        // Configure decoder (explicit CodingKeys in models handle snake_case)
        decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        // Configure encoder (explicit CodingKeys in models handle snake_case)
        encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        // Configure session
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 15
        config.timeoutIntervalForResource = 30
        config.waitsForConnectivity = true
        session = URLSession(configuration: config)
    }
    
    // MARK: - Public API
    
    /// Fetch data with retry and caching support
    func fetch<T: Decodable>(
        _ endpoint: Endpoint,
        cachePolicy: CachePolicy = .networkFirst
    ) async throws -> T {
        
        // Check cache first if policy allows
        if cachePolicy == .cacheFirst || cachePolicy == .cacheOnly {
            if let cached: T = await cache.get(for: endpoint.cacheKey) {
                return cached
            }
            if cachePolicy == .cacheOnly {
                throw APIError.noCache
            }
        }
        
        // Network request with retry
        var lastError: Error = APIError.unknown
        
        for attempt in 1...retryPolicy.maxAttempts {
            do {
                let result: T = try await performRequest(endpoint)
                
                // Cache successful response
                if endpoint.isCacheable, let encodable = result as? (any Encodable) {
                    await cache.setAny(encodable, for: endpoint.cacheKey, ttl: endpoint.cacheTTL)
                }
                
                return result
            } catch let error as APIError where error.isRetryable(policy: retryPolicy) {
                lastError = error
                
                if attempt < retryPolicy.maxAttempts {
                    let delay = retryPolicy.delay(for: attempt)
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            } catch {
                // Non-retryable error, try cache fallback
                if cachePolicy != .networkOnly, let cached: T = await cache.get(for: endpoint.cacheKey) {
                    return cached
                }
                throw error
            }
        }
        
        // All retries failed, try cache fallback
        if cachePolicy != .networkOnly, let cached: T = await cache.get(for: endpoint.cacheKey) {
            return cached
        }
        
        throw lastError
    }
    
    // MARK: - Private Methods
    
    private func performRequest<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        resolveBaseURLIfNeeded()

        var urlComponents = URLComponents(url: baseURL.appendingPathComponent(endpoint.path), resolvingAgainstBaseURL: true)!
        
        // Add query parameters
        if !endpoint.queryItems.isEmpty {
            urlComponents.queryItems = endpoint.queryItems
        }
        
        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Local-first mode does not inject an auth token.
        
        // Add body if present
        if let body = endpoint.body {
            request.httpBody = try encoder.encode(body)
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        // Handle error status codes
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(
                statusCode: httpResponse.statusCode,
                data: data,
                message: parseErrorMessage(from: data)
            )
        }
        
        // Decode response
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }

    private func resolveBaseURLIfNeeded() {
        guard !isBaseURLResolved else { return }
        isBaseURLResolved = true

        let fallback = baseURL
        let urlString = (Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String)
            ?? fallback.absoluteString

        guard let url = URL(string: urlString),
              let scheme = url.scheme,
              scheme == "https" || scheme == "http" else {
            DebugLog.error("Invalid API_BASE_URL: \(urlString). Falling back to \(fallback.absoluteString)")
            baseURL = fallback
            return
        }

        baseURL = url
    }
    
    private func parseErrorMessage(from data: Data) -> String? {
        // Common error shapes:
        // - {"detail":"..."}
        // - {"detail":{"code":"...","message":"...","missing":[...]}}
        // - {"detail":[{"loc":[...],"msg":"...","type":"..."}]}
        // - {"message":"..."}

        struct ErrorResponseString: Decodable {
            let detail: String?
            let message: String?
        }

        if let errorResponse = try? decoder.decode(ErrorResponseString.self, from: data) {
            return errorResponse.detail ?? errorResponse.message
        }

        struct ErrorDetailObject: Decodable {
            let code: String?
            let message: String?
            let missing: [String]?
            let field: String?
        }

        struct ErrorResponseObject: Decodable {
            let detail: ErrorDetailObject?
            let message: String?
        }

        if let errorResponse = try? decoder.decode(ErrorResponseObject.self, from: data) {
            if let message = errorResponse.detail?.message ?? errorResponse.message {
                if let missing = errorResponse.detail?.missing, !missing.isEmpty {
                    return "\(message) Missing: \(missing.joined(separator: ", "))."
                }
                return message
            }
        }

        struct ValidationIssue: Decodable {
            let loc: [AnyCodable]?
            let msg: String?
        }

        struct ErrorResponseValidation: Decodable {
            let detail: [ValidationIssue]?
        }

        if let errorResponse = try? decoder.decode(ErrorResponseValidation.self, from: data),
           let detail = errorResponse.detail,
           !detail.isEmpty {
            let messages = detail.compactMap { issue -> String? in
                let msg = issue.msg?.trimmingCharacters(in: .whitespacesAndNewlines)
                guard let msg, !msg.isEmpty else { return nil }
                if let loc = issue.loc, !loc.isEmpty {
                    let locString = loc.map { $0.description }.joined(separator: ".")
                    return "\(locString): \(msg)"
                }
                return msg
            }
            if !messages.isEmpty {
                return messages.prefix(2).joined(separator: " • ")
            }
        }

        // Last resort: parse arbitrary JSON and attempt to extract a useful message.
        if let object = try? JSONSerialization.jsonObject(with: data),
           let message = extractBestMessage(from: object) {
            return message
        }

        return nil
    }

    private func extractBestMessage(from object: Any) -> String? {
        if let dict = object as? [String: Any] {
            if let message = dict["message"] as? String, !message.isEmpty {
                return message
            }
            if let detail = dict["detail"] {
                // FastAPI: {"detail": {"code":..., "message":..., "missing":[...]}}
                if let detailDict = detail as? [String: Any] {
                    if let msg = detailDict["message"] as? String, !msg.isEmpty {
                        if let missing = detailDict["missing"] as? [String], !missing.isEmpty {
                            return "\(msg) Missing: \(missing.joined(separator: ", "))."
                        }
                        return msg
                    }
                    // Some endpoints: {"detail":{"error":{"message":"..."}}}
                    if let nested = extractBestMessage(from: detailDict) {
                        return nested
                    }
                }
                // FastAPI validation: {"detail":[{"msg":"..."}]}
                if let detailArr = detail as? [[String: Any]] {
                    let msgs = detailArr.compactMap { $0["msg"] as? String }.filter { !$0.isEmpty }
                    if let first = msgs.first { return first }
                }
            }
            // Nested error object
            if let err = dict["error"] {
                if let nested = extractBestMessage(from: err) { return nested }
            }
        }
        return nil
    }
}

// MARK: - AnyCodable (minimal)

private struct AnyCodable: Decodable, CustomStringConvertible {
    let value: Any

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let str = try? container.decode(String.self) {
            value = str
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let dbl = try? container.decode(Double.self) {
            value = dbl
        } else if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if container.decodeNil() {
            value = NSNull()
        } else {
            value = "<unknown>"
        }
    }

    var description: String {
        if value is NSNull { return "null" }
        return String(describing: value)
    }
}

// MARK: - Cache Policy

enum CachePolicy {
    /// Never use cache
    case networkOnly
    /// Try network first, fallback to cache
    case networkFirst
    /// Try cache first, fallback to network
    case cacheFirst
    /// Only use cache, throw if not available
    case cacheOnly
}

// MARK: - API Error

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case noCache
    case unknown
    case httpError(statusCode: Int, data: Data?, message: String?)
    case decodingError(Error)
    
    var statusCode: Int? {
        if case .httpError(let code, _, _) = self {
            return code
        }
        return nil
    }
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid server response"
        case .noCache:
            return "No cached data available"
        case .unknown:
            return "An unknown error occurred"
        case .httpError(let statusCode, _, let message):
            if let message = message {
                return message
            }
            switch statusCode {
            case 401: return "Please sign in to continue"
            case 403: return "You don't have permission for this action"
            case 404: return "The requested resource was not found"
            case 429: return "Too many requests. Please wait a moment"
            case 500...599: return "Server error. Please try again later"
            default: return "Request failed with status \(statusCode)"
            }
        case .decodingError(let error):
            return "Failed to process response: \(error.localizedDescription)"
        }
    }
    
    func isRetryable(policy: RetryPolicy) -> Bool {
        guard let code = statusCode else { return false }
        return policy.retryableStatusCodes.contains(code)
    }
}
