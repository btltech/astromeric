import XCTest

final class AstroNumericUITests: XCTestCase {
    
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func launchApp(twoProfiles: Bool = false, hideSensitive: Bool = false) -> XCUIApplication {
        let app = XCUIApplication()
        app.launchArguments = ["-ui_testing", "-ui_testing_reset"]
        app.launchArguments.append(twoProfiles ? "-ui_testing_profiles_2" : "-ui_testing_profile")
        if hideSensitive {
            app.launchArguments.append("-ui_testing_hide_sensitive")
        }
        app.launch()
        return app
    }

    private func waitForTabBar(in app: XCUIApplication, timeout: TimeInterval = 10) {
        XCTAssertTrue(app.tabBars.firstMatch.waitForExistence(timeout: timeout))
    }
    
    func testLaunchPerformance() throws {
        if #available(macOS 10.15, iOS 13.0, tvOS 13.0, watchOS 7.0, *) {
            measure(metrics: [XCTApplicationLaunchMetric()]) {
                XCUIApplication().launch()
            }
        }
    }
    
    func testOnboardingFlow() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Look for welcome view elements
        let continueAsGuestButton = app.buttons["Continue as Guest"]
        
        // If welcome view is shown
        if continueAsGuestButton.waitForExistence(timeout: 5) {
            continueAsGuestButton.tap()
            
            // Should show onboarding
            let nameTextField = app.textFields["Enter your name"]
            XCTAssertTrue(nameTextField.waitForExistence(timeout: 3))
        }
    }

    func testSmokeExploreToolsNavigation() throws {
        let app = launchApp(twoProfiles: false)
        waitForTabBar(in: app)

        app.tabBars.buttons["Tools"].tap()
        XCTAssertTrue(app.navigationBars["Cosmic Tools"].waitForExistence(timeout: 2))

        // Tarot
        app.staticTexts["Tarot"].tap()
        XCTAssertTrue(app.navigationBars["Daily Tarot"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        // Moon Phase
        app.staticTexts["Moon Phase"].tap()
        XCTAssertTrue(app.navigationBars["Moon Phase"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        // Timing Advisor
        app.swipeUp()
        app.staticTexts["Timing"].tap()
        XCTAssertTrue(app.navigationBars["Timing Advisor"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()
    }

    func testSmokeChartsAdvancedNavigation() throws {
        let app = launchApp(twoProfiles: true)
        waitForTabBar(in: app)

        app.tabBars.buttons["Charts"].tap()
        XCTAssertTrue(app.navigationBars["Charts"].waitForExistence(timeout: 2))

        let advancedButton = app.buttons["Advanced"].firstMatch
        if advancedButton.waitForExistence(timeout: 2) {
            advancedButton.tap()
        } else {
            app.staticTexts["Advanced"].firstMatch.tap()
        }

        app.staticTexts["Synastry"].firstMatch.tap()
        XCTAssertTrue(app.navigationBars["Synastry"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        app.staticTexts["Composite Chart"].firstMatch.tap()
        XCTAssertTrue(app.navigationBars["Composite Chart"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        app.staticTexts["Progressions"].firstMatch.tap()
        XCTAssertTrue(app.navigationBars["Progressions"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()
    }

    func testSmokeProfileSwitching() throws {
        let app = launchApp(twoProfiles: true)
        waitForTabBar(in: app)

        app.tabBars.buttons["Profile"].tap()
        XCTAssertTrue(app.navigationBars["Profile"].waitForExistence(timeout: 2))

        XCTAssertTrue(app.staticTexts["ABIOLA BOLAJI"].waitForExistence(timeout: 2))
        let partnerButton = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Test Partner")).firstMatch
        XCTAssertTrue(partnerButton.waitForExistence(timeout: 3))
        partnerButton.tap()
        XCTAssertTrue(app.staticTexts["Test Partner"].waitForExistence(timeout: 2))
    }

    func testPrivacyModeMasksProfileLabels() throws {
        let app = launchApp(twoProfiles: true, hideSensitive: true)
        waitForTabBar(in: app)

        app.tabBars.buttons["Profile"].tap()
        XCTAssertTrue(app.navigationBars["Profile"].waitForExistence(timeout: 2))

        XCTAssertTrue(app.staticTexts["You"].waitForExistence(timeout: 2))
        XCTAssertFalse(app.staticTexts["ABIOLA BOLAJI"].exists)
        XCTAssertFalse(app.buttons["Test Partner"].exists)
        XCTAssertTrue(app.buttons["Profile 2"].waitForExistence(timeout: 2))
    }
}
