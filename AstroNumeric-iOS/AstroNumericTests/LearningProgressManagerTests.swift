import XCTest
@testable import AstroNumeric

final class LearningProgressManagerTests: XCTestCase {
    
    private var manager: LearningProgressManager!
    
    override func setUp() {
        super.setUp()
        manager = LearningProgressManager.shared
        manager.resetAll()
    }
    
    override func tearDown() {
        manager.resetAll()
        super.tearDown()
    }
    
    // MARK: - Mark Complete Tests
    
    func testMarkCompleteAddsModuleId() {
        manager.markComplete(moduleId: "astro-1")
        XCTAssertTrue(manager.isComplete(moduleId: "astro-1"))
    }
    
    func testMarkCompleteDuplicateIsIdempotent() {
        manager.markComplete(moduleId: "astro-1")
        manager.markComplete(moduleId: "astro-1")
        XCTAssertTrue(manager.isComplete(moduleId: "astro-1"))
        XCTAssertEqual(manager.completedModuleIds.count, 1)
    }
    
    func testIsCompleteReturnsFalseForUncompletedModule() {
        XCTAssertFalse(manager.isComplete(moduleId: "astro-99"))
    }
    
    // MARK: - Progress Calculation Tests
    
    func testProgressReturnsZeroForNoCompletions() {
        let progress = manager.progress(for: LearningTrack.astrology101LessonIds)
        XCTAssertEqual(progress, 0.0)
    }
    
    func testProgressReturnsCorrectFraction() {
        manager.markComplete(moduleId: "astro-1")
        manager.markComplete(moduleId: "astro-2")
        manager.markComplete(moduleId: "astro-3")
        let progress = manager.progress(for: LearningTrack.astrology101LessonIds)
        XCTAssertEqual(progress, 3.0 / 12.0, accuracy: 0.001)
    }
    
    func testProgressReturnsOneWhenAllComplete() {
        for id in LearningTrack.moonWisdomLessonIds {
            manager.markComplete(moduleId: id)
        }
        let progress = manager.progress(for: LearningTrack.moonWisdomLessonIds)
        XCTAssertEqual(progress, 1.0, accuracy: 0.001)
    }
    
    func testProgressReturnsZeroForEmptyLessonIds() {
        let progress = manager.progress(for: [])
        XCTAssertEqual(progress, 0.0)
    }
    
    func testProgressIgnoresUnrelatedCompletions() {
        manager.markComplete(moduleId: "tarot-1")
        let progress = manager.progress(for: LearningTrack.astrology101LessonIds)
        XCTAssertEqual(progress, 0.0)
    }
    
    // MARK: - Completed Count Tests
    
    func testCompletedCountReturnsCorrectCount() {
        manager.markComplete(moduleId: "numerology-1")
        manager.markComplete(moduleId: "numerology-3")
        let count = manager.completedCount(from: LearningTrack.numerologyBasicsLessonIds)
        XCTAssertEqual(count, 2)
    }
    
    // MARK: - Reset Tests
    
    func testResetAllClearsAllProgress() {
        manager.markComplete(moduleId: "astro-1")
        manager.markComplete(moduleId: "tarot-1")
        manager.resetAll()
        XCTAssertFalse(manager.isComplete(moduleId: "astro-1"))
        XCTAssertFalse(manager.isComplete(moduleId: "tarot-1"))
        XCTAssertEqual(manager.completedModuleIds.count, 0)
    }
    
    // MARK: - Learning Track ID Tests
    
    func testLearningTrackIdCounts() {
        XCTAssertEqual(LearningTrack.astrology101LessonIds.count, 12)
        XCTAssertEqual(LearningTrack.numerologyBasicsLessonIds.count, 8)
        XCTAssertEqual(LearningTrack.moonWisdomLessonIds.count, 6)
        XCTAssertEqual(LearningTrack.tarotMasteryLessonIds.count, 10)
    }
    
    func testLearningTrackIdFormat() {
        XCTAssertEqual(LearningTrack.astrology101LessonIds.first, "astro-1")
        XCTAssertEqual(LearningTrack.astrology101LessonIds.last, "astro-12")
        XCTAssertEqual(LearningTrack.numerologyBasicsLessonIds.first, "numerology-1")
        XCTAssertEqual(LearningTrack.tarotMasteryLessonIds.last, "tarot-10")
    }
}
