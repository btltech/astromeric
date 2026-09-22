import XCTest
@testable import AstroNumeric

final class AIAccessCodeTests: XCTestCase {
    /// Separate Keychain service so tests never touch the real access code.
    private let service = "com.astromeric.app.ai-access.tests"

    override func setUp() {
        super.setUp()
        AIAccessCode.clear(service: service)
    }

    override func tearDown() {
        AIAccessCode.clear(service: service)
        super.tearDown()
    }

    func testNoCodeIsStoredByDefault() {
        XCTAssertNil(AIAccessCode.current(service: service))
    }

    func testStoredCodeIsReadBack() {
        XCTAssertTrue(AIAccessCode.set("s3cret-code", service: service))
        XCTAssertEqual(AIAccessCode.current(service: service), "s3cret-code")
    }

    func testSavingAgainReplacesTheStoredCode() {
        AIAccessCode.set("first", service: service)
        AIAccessCode.set("second", service: service)
        XCTAssertEqual(AIAccessCode.current(service: service), "second")
    }

    func testCodeIsTrimmedAndBlankInputClearsIt() {
        AIAccessCode.set("  padded  ", service: service)
        XCTAssertEqual(AIAccessCode.current(service: service), "padded")

        AIAccessCode.set("   ", service: service)
        XCTAssertNil(AIAccessCode.current(service: service))
    }

    func testClearRemovesTheCode() {
        AIAccessCode.set("s3cret-code", service: service)
        AIAccessCode.clear(service: service)
        XCTAssertNil(AIAccessCode.current(service: service))
    }
}
