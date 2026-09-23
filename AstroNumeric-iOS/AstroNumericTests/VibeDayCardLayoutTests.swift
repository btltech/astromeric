import XCTest
import SwiftUI
@testable import AstroNumeric

/// The weekly pulse cards were pinned to a fixed 70x110 frame, so the bottom row
/// — the day's score — was clipped, most visibly on the highlighted "today" card.
/// These tests render the card and check it is tall enough to hold its content,
/// including at accessibility text sizes.
@MainActor
final class VibeDayCardLayoutTests: XCTestCase {

    private func makeDay(date: String) -> ForecastDay {
        ForecastDay(date: date, score: 77, vibe: "Favorable", icon: "✨", recommendation: "Keep going")
    }

    private func render(_ day: ForecastDay, typeSize: DynamicTypeSize) throws -> UIImage {
        let renderer = ImageRenderer(
            content: VibeDayCard(day: day)
                .environment(\.dynamicTypeSize, typeSize)
                .environment(\.colorScheme, .dark)
        )
        renderer.scale = 2
        return try XCTUnwrap(renderer.uiImage)
    }

    private func todayString() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: Date())
    }

    func testTodayCardIsNotShorterThanTheOtherDays() throws {
        // The highlighted card carries the same rows plus a border; when the frame
        // was fixed, this is the one that lost its score row.
        let today = try render(makeDay(date: todayString()), typeSize: .large)
        let other = try render(makeDay(date: "2030-01-01"), typeSize: .large)
        XCTAssertEqual(today.size.height, other.size.height, accuracy: 1.0)
    }

    func testCardGrowsWithAccessibilityTextSizes() throws {
        let standard = try render(makeDay(date: "2030-01-01"), typeSize: .large)
        let accessible = try render(makeDay(date: "2030-01-01"), typeSize: .accessibility3)

        // A fixed-height card would render identically and clip its content.
        XCTAssertGreaterThan(
            accessible.size.height, standard.size.height,
            "Card height ignores Dynamic Type, so its score row will be clipped"
        )
    }
}
