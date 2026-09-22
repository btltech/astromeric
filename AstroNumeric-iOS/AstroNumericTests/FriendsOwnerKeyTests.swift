import XCTest
@testable import AstroNumeric

final class FriendsOwnerKeyTests: XCTestCase {
    /// Separate Keychain service so tests never touch the app's real install secret.
    private let service = "com.astromeric.app.friends-owner.tests"

    override func setUp() {
        super.setUp()
        FriendsOwnerKey.deleteSecret(service: service)
    }

    override func tearDown() {
        FriendsOwnerKey.deleteSecret(service: service)
        super.tearDown()
    }

    /// Mirrors the backend's accepted format (backend/app/routers/friends.py).
    private func matchesBackendOwnerKeyFormat(_ value: String) -> Bool {
        value.range(of: "^[0-9a-f]{32,64}$", options: .regularExpression) != nil
    }

    func testOwnerIdIsSixtyFourLowercaseHexAcceptedByBackend() throws {
        let ownerId = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -1, service: service))
        XCTAssertEqual(ownerId.count, 64)
        XCTAssertTrue(matchesBackendOwnerKeyFormat(ownerId))
    }

    func testOwnerIdIsStableAcrossCallsForTheSameProfile() throws {
        let first = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -1, service: service))
        let second = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -1, service: service))
        XCTAssertEqual(first, second)
    }

    func testEachProfileGetsItsOwnOwnerId() throws {
        let a = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -1, service: service))
        let b = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -2, service: service))
        XCTAssertNotEqual(a, b)
    }

    func testDifferentInstallsProduceDifferentOwnerIdsForTheSameLocalProfileId() {
        // Every device's first profile is -1; the install secret must keep them apart.
        let installA = Data(repeating: 0x01, count: 32)
        let installB = Data(repeating: 0x02, count: 32)
        XCTAssertNotEqual(
            FriendsOwnerKey.derive(secret: installA, profileId: -1),
            FriendsOwnerKey.derive(secret: installB, profileId: -1)
        )
    }

    func testInstallSecretIsPersistedAndReused() throws {
        let created = try XCTUnwrap(FriendsOwnerKey.installSecret(service: service))
        XCTAssertEqual(created.count, 32)
        XCTAssertEqual(FriendsOwnerKey.installSecret(service: service), created)
    }

    func testOwnerIdNeverContainsTheLocalProfileId() throws {
        let ownerId = try XCTUnwrap(FriendsOwnerKey.ownerId(forProfileId: -1, service: service))
        XCTAssertNotEqual(ownerId, "-1")
        XCTAssertFalse(ownerId.contains("-"))
    }
}
