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
        XCTAssertEqual(progress, 3.0 / Double(LearningTrack.astrology101LessonIds.count), accuracy: 0.001)
    }
    
    func testProgressReturnsOneWhenAllComplete() {
        for id in LearningTrack.signsAndElementsLessonIds {
            manager.markComplete(moduleId: id)
        }
        let progress = manager.progress(for: LearningTrack.signsAndElementsLessonIds)
        XCTAssertEqual(progress, 1.0, accuracy: 0.001)
    }
    
    func testProgressReturnsZeroForEmptyLessonIds() {
        let progress = manager.progress(for: [])
        XCTAssertEqual(progress, 0.0)
    }
    
    func testProgressIgnoresUnrelatedCompletions() {
        manager.markComplete(moduleId: "num-1")
        let progress = manager.progress(for: LearningTrack.astrology101LessonIds)
        XCTAssertEqual(progress, 0.0)
    }
    
    // MARK: - Completed Count Tests
    
    func testCompletedCountReturnsCorrectCount() {
        manager.markComplete(moduleId: "num-1")
        manager.markComplete(moduleId: "num-3")
        let count = manager.completedCount(from: LearningTrack.numerologyBasicsLessonIds)
        XCTAssertEqual(count, 2)
    }
    
    // MARK: - Reset Tests
    
    func testResetAllClearsAllProgress() {
        manager.markComplete(moduleId: "astro-1")
        manager.markComplete(moduleId: "num-1")
        manager.resetAll()
        XCTAssertFalse(manager.isComplete(moduleId: "astro-1"))
        XCTAssertFalse(manager.isComplete(moduleId: "num-1"))
        XCTAssertEqual(manager.completedModuleIds.count, 0)
    }
    
    // MARK: - Learning Track ID Tests
    
    func testEveryTrackLessonExists() {
        // A track may only count lessons the app actually has; the old tracks
        // advertised 36 lessons across four tracks against 14 real ones.
        let vm = LearnVM()
        let real = Set(["astrology", "numerology", "zodiac", "elements"]
            .flatMap { vm.fallbackModules(for: $0) }
            .map(\.id))
        let tracks = [
            LearningTrack.astrology101LessonIds,
            LearningTrack.signsAndElementsLessonIds,
            LearningTrack.numerologyBasicsLessonIds,
        ]
        for track in tracks {
            XCTAssertFalse(track.isEmpty)
            XCTAssertTrue(Set(track).isSubset(of: real), "missing: \(Set(track).subtracting(real))")
        }
        XCTAssertEqual(Set(tracks.flatMap { $0 }), real, "every lesson belongs to a track")
    }
}
