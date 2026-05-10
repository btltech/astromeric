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

    private func launchAppWithoutProfiles() -> XCUIApplication {
        let app = XCUIApplication()
        app.launchArguments = ["-ui_testing", "-ui_testing_reset", "-ui_testing_no_profiles"]
        app.launch()
        return app
    }

    private func reveal(_ element: XCUIElement, in app: XCUIApplication, swipes: Int = 5) -> Bool {
        if element.waitForExistence(timeout: 1) { return true }
        for _ in 0..<swipes {
            let scrollTarget = app.scrollViews.firstMatch.exists ? app.scrollViews.firstMatch : app
            scrollTarget.swipeUp()
            if element.waitForExistence(timeout: 1) { return true }
        }
        return element.exists
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

    func testFirstRunProfileCreation() throws {
        let app = launchAppWithoutProfiles()

        let promptButton = app.buttons["Create Profile"]
        XCTAssertTrue(promptButton.waitForExistence(timeout: 5))
        promptButton.tap()

        let nameField = app.textFields["Profile name"]
        XCTAssertTrue(nameField.waitForExistence(timeout: 5))
        nameField.tap()
        nameField.typeText("New Native Profile")

        let placeField = app.textFields["Birth place"]
        XCTAssertTrue(placeField.waitForExistence(timeout: 2))
        placeField.tap()
        placeField.typeText("Lagos, Nigeria")

        let createButton = app.buttons["Create profile"]
        XCTAssertTrue(createButton.waitForExistence(timeout: 2))
        XCTAssertTrue(createButton.isEnabled)
    }

    func testDailyGuideNavigation() throws {
        let app = launchApp(twoProfiles: false)
        waitForTabBar(in: app)

        app.tabBars.buttons["Tools"].tap()
        XCTAssertTrue(app.navigationBars["Cosmic Tools"].waitForExistence(timeout: 2))

        let dailyGuideButton = app.staticTexts["Daily Guide"].firstMatch
        XCTAssertTrue(reveal(dailyGuideButton, in: app))
        dailyGuideButton.tap()
        XCTAssertTrue(app.otherElements["DailyGuideScreen"].waitForExistence(timeout: 3))
    }

    func testChartRenderingShowsBirthChartSurface() throws {
        let app = launchApp(twoProfiles: false)
        waitForTabBar(in: app)

        app.tabBars.buttons["Charts"].tap()
        XCTAssertTrue(app.navigationBars["Charts"].waitForExistence(timeout: 2))
        XCTAssertTrue(app.staticTexts["Birth Chart"].waitForExistence(timeout: 3))
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

        app.buttons["Synastry"].firstMatch.tap()
        XCTAssertTrue(app.otherElements["SynastryScreen"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        app.buttons["Composite Chart"].firstMatch.tap()
        XCTAssertTrue(app.navigationBars["Composite Chart"].waitForExistence(timeout: 3))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        app.buttons["Progressions"].firstMatch.tap()
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

    func testProfileDiagnosticsNotificationSettingsAndPrivacyExport() throws {
        let app = launchApp(twoProfiles: true, hideSensitive: true)
        waitForTabBar(in: app)

        app.tabBars.buttons["Profile"].tap()
        XCTAssertTrue(app.navigationBars["Profile"].waitForExistence(timeout: 2))

        XCTAssertTrue(app.switches["Hide Sensitive Details"].waitForExistence(timeout: 3))

        let refreshDiagnostics = app.buttons["Refresh diagnostics"].firstMatch
        XCTAssertTrue(reveal(refreshDiagnostics, in: app, swipes: 2))
        XCTAssertTrue(app.staticTexts["Notifications"].waitForExistence(timeout: 2))
        XCTAssertTrue(app.staticTexts["Widget Refresh"].waitForExistence(timeout: 2))

        let privacyPolicy = app.buttons["Privacy Policy"].firstMatch
        XCTAssertTrue(reveal(privacyPolicy, in: app))
        privacyPolicy.tap()
        XCTAssertTrue(app.navigationBars["Privacy"].waitForExistence(timeout: 3))
        XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "network-backed features")).firstMatch.waitForExistence(timeout: 2))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        let exportButton = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Export")).firstMatch
        XCTAssertTrue(reveal(exportButton, in: app))
    }
}
