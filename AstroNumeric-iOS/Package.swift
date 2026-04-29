// swift-tools-version: 5.9
// Package.swift - Use Swift Package Manager for development

import PackageDescription

let package = Package(
    name: "AstroNumeric",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "AstroNumeric",
            targets: ["AstroNumeric"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "AstroNumeric",
            dependencies: [],
            path: "AstroNumeric",
            exclude: [
                "Features/Reading/Components/AIInsightsSheetView.swift"
            ]
        )
    ]
)
