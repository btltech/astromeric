// AstroWidgetBundle.swift
// Widget Extension entry point — bundles all widget types.

import WidgetKit
import SwiftUI

@main
struct AstroWidgetBundle: WidgetBundle {
    var body: some Widget {
        PlanetaryHourWidget()
        MoonPhaseWidget()
        DailySummaryWidget()
        MorningBriefWidget()
    }
}
