import XCTest
import SwiftUI
@testable import AstroNumeric

/// Share cards are drawn by `ImageRenderer`, which renders in its own environment
/// rather than the app's. A card that paints `Color(.systemBackground)` therefore
/// came out **white**, under text using the app's near-white tokens, so every
/// image a user shared was unreadable. These tests pin the two facts that bug
/// depended on.
@MainActor
final class ShareCardRenderingTests: XCTestCase {

    private func makeReading() -> PredictionData {
        PredictionData(
            profile: nil,
            scope: "daily",
            date: "2026-09-23",
            sections: [
                ForecastSection(
                    title: "Overview",
                    summary: "A steady day for finishing what is already open.",
                    topics: ["career": 0.8],
                    avoid: ["Starting something new"],
                    embrace: ["Closing loops"]
                )
            ],
            overallScore: 7.4,
            generatedAt: "2026-09-23T00:00:00Z"
        )
    }

    /// Mean luminance of the image, 0 (black) to 1 (white).
    private func averageLuminance(of image: UIImage) throws -> CGFloat {
        let cgImage = try XCTUnwrap(image.cgImage)
        let width = 1, height = 1
        var pixel = [UInt8](repeating: 0, count: 4)
        let context = try XCTUnwrap(CGContext(
            data: &pixel,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ))
        // Drawing the whole card into a 1x1 context averages every pixel.
        context.interpolationQuality = .medium
        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
        let r = CGFloat(pixel[0]) / 255, g = CGFloat(pixel[1]) / 255, b = CGFloat(pixel[2]) / 255
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }

    func testExportedShareCardIsDarkEnoughForItsText() throws {
        let image = try XCTUnwrap(ShareCardGenerator.generateImage(for: makeReading()))
        let luminance = try averageLuminance(of: image)

        // The card's text uses Color.textPrimary/textSecondary (0.85–0.96 white).
        // Anything but a dark card makes that text unreadable; the broken build
        // measured ~0.95 here.
        XCTAssertLessThan(
            luminance, 0.35,
            "Share card background is too light (\(luminance)) for its near-white text"
        )

        // Written out so the image can be inspected by eye as well as measured.
        let url = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("share-card-reading.png")
        if let data = image.pngData() {
            try? data.write(to: url)
            print("SHARE_CARD_PNG=\(url.path)")
        }
    }

    func testSystemBackgroundStillResolvesLightInImageRenderer() throws {
        // The reason the app's own dark tokens are required rather than
        // Color(.systemBackground): the renderer does not inherit the app's dark
        // lock. If a future OS changes this, this test tells us why the
        // workaround exists.
        let renderer = ImageRenderer(
            content: Color(.systemBackground).frame(width: 40, height: 40)
        )
        let image = try XCTUnwrap(renderer.uiImage)
        XCTAssertGreaterThan(
            try averageLuminance(of: image), 0.8,
            "systemBackground no longer renders light here — the token workaround can be revisited"
        )
    }
}
