// MoreChartsViews.swift
// Solar arc, relocation, lunar return, profections, declinations and fixed stars.

import SwiftUI
import CoreLocation
import MapKit

// MARK: - Shared loader and layout

@Observable
final class AdvancedChartLoader<T: Decodable> {
    var value: T?
    var isLoading = false
    var error: String?

    @MainActor
    func load(_ endpoint: Endpoint) async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let response: V2ApiResponse<T> = try await APIClient.shared.fetch(endpoint, cachePolicy: .networkFirst)
            value = response.data
        } catch {
            value = nil
            self.error = error.localizedDescription
        }
    }
}

/// Background, header and scroll view shared by the six screens.
private struct AdvancedChartScaffold<Content: View>: View {
    let eyebrow: String
    let title: String
    let subtitle: String
    @ViewBuilder var content: () -> Content

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: Space.md) {
                    PremiumScreenHeader(eyebrow: eyebrow, title: title, subtitle: subtitle, accent: .accentPrimary)
                    content()
                }
                .padding()
                .readableContainer()
            }
            .scrollDismissesKeyboard(.interactively)
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct NeedsProfileCard: View {
    var body: some View {
        CardView {
            Text("Add your birth profile first. These charts are worked out from your birth date, time and place.")
                .font(.subtext)
                .foregroundStyle(Color.textSecondary)
        }
    }
}

private struct ApproximateChartNote: View {
    let profile: Profile?

    var body: some View {
        if let profile, profile.dataQuality != .full {
            DataQualityBanner(
                icon: "clock.badge.questionmark",
                message: "This chart is less precise without an exact birth time and place. Add them in Profile for exact houses.",
                color: .yellow
            )
        }
    }
}

private struct LoadStateView<T: Decodable, Result: View>: View {
    let loader: AdvancedChartLoader<T>
    let retry: () async -> Void
    @ViewBuilder var result: (T) -> Result

    var body: some View {
        if loader.isLoading {
            ProgressView("Calculating…")
                .tint(.white)
                .frame(maxWidth: .infinity)
        } else if let error = loader.error {
            ErrorStateView(message: error) { await retry() }
        } else if let value = loader.value {
            result(value)
        }
    }
}

private struct PlanetRowsCard: View {
    let title: String
    let planets: [AdvancedChartPlanet]
    var showHouse = true

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 8) {
                Text(title).font(.headline)
                ForEach(planets) { planet in
                    HStack {
                        Text(planet.name + (planet.retrograde == true ? " ℞" : ""))
                        Spacer()
                        Text(position(planet))
                            .foregroundStyle(Color.textSecondary)
                    }
                    .font(.subheadline)
                    .accessibilityElement(children: .combine)
                }
            }
        }
    }

    private func position(_ planet: AdvancedChartPlanet) -> String {
        var text = "\(planet.sign) \(String(format: "%.1f", planet.degree))°"
        if showHouse, let house = planet.house {
            text += " · house \(house)"
        }
        return text
    }
}

private struct AspectRowsCard: View {
    let title: String
    let aspects: [AdvancedChartAspect]

    var body: some View {
        if !aspects.isEmpty {
            CardView {
                VStack(alignment: .leading, spacing: 8) {
                    Text(title).font(.headline)
                    ForEach(aspects.prefix(12)) { aspect in
                        HStack(alignment: .firstTextBaseline) {
                            Text("\(aspect.planetA) \(aspect.type.replacingOccurrences(of: "_", with: " ")) \(aspect.planetB)")
                            Spacer()
                            if let orb = aspect.orb {
                                Text("\(String(format: "%.1f", orb))° orb")
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        .font(.subheadline)
                        .accessibilityElement(children: .combine)
                    }
                }
            }
        }
    }
}

private func readableDate(_ iso: String?) -> String? {
    guard let iso else { return nil }
    let parser = ISO8601DateFormatter()
    parser.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    let plain = ISO8601DateFormatter()
    // The server's local time carries its own offset; show it as written, not shifted.
    guard let date = parser.date(from: iso) ?? plain.date(from: iso) else { return iso }
    let out = DateFormatter()
    out.dateStyle = .medium
    out.timeStyle = .short
    out.timeZone = TimeZone(iso8601Offset: iso) ?? .current
    return out.string(from: date)
}

private extension TimeZone {
    /// Reads a trailing "+01:00" / "-05:00" / "Z" so a time is shown where it happened.
    init?(iso8601Offset iso: String) {
        if iso.hasSuffix("Z") {
            self.init(secondsFromGMT: 0)
            return
        }
        guard iso.count >= 6 else { return nil }
        let tail = String(iso.suffix(6))
        guard let sign = tail.first, sign == "+" || sign == "-", tail[tail.index(tail.startIndex, offsetBy: 3)] == ":" else {
            return nil
        }
        let hours = Int(tail.dropFirst().prefix(2)) ?? 0
        let minutes = Int(tail.suffix(2)) ?? 0
        let seconds = (hours * 3600 + minutes * 60) * (sign == "-" ? -1 : 1)
        self.init(secondsFromGMT: seconds)
    }
}

// MARK: - Solar arc

struct SolarArcView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<AdvancedChartResponse>()
    @State private var targetDate = Date()

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Timing",
            title: "Solar Arc",
            subtitle: "Every planet moved forward by the same arc as your progressed Sun, about a degree a year."
        ) {
            if let profile = store.activeProfile {
                ApproximateChartNote(profile: profile)
                DatePicker("Directed to", selection: $targetDate, displayedComponents: .date)
                LoadStateView(loader: loader, retry: { await reload() }) { chart in
                    if let meta = chart.metadata {
                        CardView {
                            VStack(alignment: .leading, spacing: 6) {
                                if let arc = meta.solarArcDegrees {
                                    Text("Solar arc: \(String(format: "%.2f", arc))°").font(.headline)
                                }
                                if let age = meta.ageYears {
                                    Text("Age \(String(format: "%.1f", age)) at \(meta.directedTo ?? "this date")")
                                        .font(.subtext)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        }
                    }
                    PlanetRowsCard(title: "Directed planets", planets: chart.planets)
                    AspectRowsCard(title: "Directed planets touching your birth chart", aspects: chart.aspects)
                }
            } else {
                NeedsProfileCard()
            }
        }
        .task(id: "\(String(describing: store.activeProfile?.id))-\(targetDate.localISODay)") { await reload() }
    }

    private func reload() async {
        guard let profile = store.activeProfile else { return }
        await loader.load(.solarArcChart(profile: profile, targetDate: targetDate))
    }
}

// MARK: - Lunar return

struct LunarReturnView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<AdvancedChartResponse>()
    @State private var fromDate = Date()

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Timing",
            title: "Lunar Return",
            subtitle: "The chart for the next moment the Moon comes back to where it was at your birth, roughly every 27 days."
        ) {
            if let profile = store.activeProfile {
                ApproximateChartNote(profile: profile)
                DatePicker("Next return after", selection: $fromDate, displayedComponents: .date)
                LoadStateView(loader: loader, retry: { await reload() }) { chart in
                    CardView {
                        VStack(alignment: .leading, spacing: 6) {
                            if let when = readableDate(chart.metadata?.returnLocal) {
                                Text(when).font(.headline)
                            }
                            if let sign = chart.metadata?.natalMoonSign, let degree = chart.metadata?.natalMoonDegree {
                                Text("Natal Moon: \(sign) \(String(format: "%.1f", degree))°")
                                    .font(.subtext)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    PlanetRowsCard(title: "Planets at the return", planets: chart.planets)
                    AspectRowsCard(title: "Aspects at the return", aspects: chart.aspects)
                }
            } else {
                NeedsProfileCard()
            }
        }
        .task(id: "\(String(describing: store.activeProfile?.id))-\(fromDate.localISODay)") { await reload() }
    }

    private func reload() async {
        guard let profile = store.activeProfile else { return }
        await loader.load(.lunarReturnChart(profile: profile, targetDate: fromDate))
    }
}

// MARK: - Relocation

private struct PlaceMatch: Identifiable {
    let id = UUID()
    let name: String
    let latitude: Double
    let longitude: Double
    let timezone: String?
}

/// Looks a place up with the system geocoder, then MapKit if that finds nothing or
/// stalls. Each step gives up after a few seconds so the screen never hangs.
private func findPlaces(_ query: String) async -> [PlaceMatch] {
    var matches = await geocodeWithSystem(query)
    if matches.isEmpty {
        matches = await searchWithMapKit(query)
    }
    // The same name can come back twice; keep one of each.
    var seen = Set<String>()
    return matches.filter { seen.insert($0.name).inserted }.prefix(5).map { $0 }
}

private func displayName(_ parts: [String?], fallback: String) -> String {
    let name = parts.compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: ", ")
    return name.isEmpty ? fallback : name
}

private func geocodeWithSystem(_ query: String) async -> [PlaceMatch] {
    let geocoder = CLGeocoder()
    let timeout = Task {
        try? await Task.sleep(for: .seconds(6))
        geocoder.cancelGeocode()
    }
    defer { timeout.cancel() }
    let marks: [CLPlacemark] = await withCheckedContinuation { continuation in
        geocoder.geocodeAddressString(query) { marks, _ in continuation.resume(returning: marks ?? []) }
    }
    return marks.compactMap { mark in
        guard let coordinate = mark.location?.coordinate else { return nil }
        return PlaceMatch(
            name: displayName([mark.locality ?? mark.name, mark.administrativeArea, mark.country], fallback: query),
            latitude: coordinate.latitude,
            longitude: coordinate.longitude,
            timezone: mark.timeZone?.identifier
        )
    }
}

private func searchWithMapKit(_ query: String) async -> [PlaceMatch] {
    let request = MKLocalSearch.Request()
    request.naturalLanguageQuery = query
    request.resultTypes = .address
    let search = MKLocalSearch(request: request)
    let timeout = Task {
        try? await Task.sleep(for: .seconds(6))
        search.cancel()
    }
    defer { timeout.cancel() }
    let items: [MKMapItem] = await withCheckedContinuation { continuation in
        search.start { response, _ in continuation.resume(returning: response?.mapItems ?? []) }
    }
    return items.map { item in
        let mark = item.placemark
        return PlaceMatch(
            name: displayName([mark.locality ?? item.name, mark.administrativeArea, mark.country], fallback: query),
            latitude: mark.coordinate.latitude,
            longitude: mark.coordinate.longitude,
            timezone: item.timeZone?.identifier
        )
    }
}

struct RelocationChartView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<AdvancedChartResponse>()
    @State private var place = ""
    @State private var choices: [PlaceMatch] = []
    @State private var resolvedName: String?
    @State private var lookupError: String?
    @State private var isLookingUp = false

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Place",
            title: "Relocation",
            subtitle: "Your birth moment cast for another place. The planets stay put; the houses and angles change."
        ) {
            if let profile = store.activeProfile {
                if profile.latitude == nil || profile.longitude == nil {
                    DataQualityBanner(
                        icon: "mappin.slash",
                        message: "Add your birthplace in Profile first, so there is a place to move the chart from.",
                        color: .yellow
                    )
                }
                CardView {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Move the chart to").font(.headline)
                        TextField("City, country", text: $place)
                            .textFieldStyle(.roundedBorder)
                            .submitLabel(.search)
                            .onSubmit { Task { await lookUp(profile: profile) } }
                        Button {
                            Task { await lookUp(profile: profile) }
                        } label: {
                            Text(isLookingUp ? "Looking up…" : "Show chart")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(isLookingUp || place.trimmingCharacters(in: .whitespaces).isEmpty)
                        if let lookupError {
                            Text(lookupError).font(.caption).foregroundStyle(.red)
                        }
                    }
                }
                if choices.count > 1 {
                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Which one?").font(.headline)
                            ForEach(choices) { choice in
                                Button(choice.name) {
                                    Task { await show(choice, profile: profile) }
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                    }
                }
                LoadStateView(loader: loader, retry: { await lookUp(profile: profile) }) { chart in
                    if let resolvedName {
                        Text("Houses for \(resolvedName)")
                            .font(.headline)
                    }
                    PlanetRowsCard(title: "Planets in the new houses", planets: chart.planets)
                }
            } else {
                NeedsProfileCard()
            }
        }
    }

    @MainActor
    private func lookUp(profile: Profile) async {
        let query = place.trimmingCharacters(in: .whitespaces)
        guard !query.isEmpty else { return }
        isLookingUp = true
        lookupError = nil
        choices = []
        defer { isLookingUp = false }
        let found = await findPlaces(query)
        switch found.count {
        case 0:
            lookupError = "No place found. Try a city and country."
        case 1:
            await show(found[0], profile: profile)
        default:
            // Names repeat across the world ("Lagos" is in Nigeria and Portugal), so ask.
            choices = found
        }
    }

    @MainActor
    private func show(_ match: PlaceMatch, profile: Profile) async {
        choices = []
        resolvedName = match.name
        await loader.load(.relocationChart(
            profile: profile,
            latitude: match.latitude,
            longitude: match.longitude,
            timezone: match.timezone
        ))
    }
}

// MARK: - Profections

struct ProfectionsView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<ProfectionsResponse>()
    @State private var refDate = Date()

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Timing",
            title: "Profections",
            subtitle: "An ancient yearly timing method: each year of life moves the spotlight to the next house, and its ruler becomes the Time Lord."
        ) {
            if let profile = store.activeProfile {
                if profile.timeOfBirth == nil || profile.latitude == nil {
                    DataQualityBanner(
                        icon: "clock.badge.questionmark",
                        message: "The Time Lord needs your exact birth time and place. Without them you still get the house for the year.",
                        color: .yellow
                    )
                }
                DatePicker("As of", selection: $refDate, displayedComponents: .date)
                LoadStateView(loader: loader, retry: { await reload() }) { data in
                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Year \(data.age + 1) of your life: house \(data.annualHouse)").font(.headline)
                            if let sign = data.annualSign, let lord = data.annualLord, !lord.isEmpty {
                                Text("\(sign) is the profected sign. Time Lord: \(lord).")
                                    .font(.subheadline)
                            }
                            if !data.annualFocus.isEmpty {
                                Text(data.annualFocus).font(.subtext).foregroundStyle(Color.textSecondary)
                            }
                            if !data.annualLordThemes.isEmpty {
                                Text(data.annualLordThemes).font(.subtext).foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("This month: house \(data.monthlyHouse)").font(.headline)
                            if let sign = data.monthlySign, let lord = data.monthlyLord, !lord.isEmpty {
                                Text("\(sign), ruled by \(lord).").font(.subheadline)
                            }
                            if !data.monthlyFocus.isEmpty {
                                Text(data.monthlyFocus).font(.subtext).foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    if !data.interpretation.isEmpty {
                        CardView {
                            Text(data.interpretation).font(.subtext).foregroundStyle(Color.textSecondary)
                        }
                    }
                }
            } else {
                NeedsProfileCard()
            }
        }
        .task(id: "\(String(describing: store.activeProfile?.id))-\(refDate.localISODay)") { await reload() }
    }

    private func reload() async {
        guard let profile = store.activeProfile else { return }
        await loader.load(.profections(profile: profile, refDate: refDate))
    }
}

// MARK: - Declinations

struct DeclinationsView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<DeclinationsResponse>()

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Chart",
            title: "Declinations",
            subtitle: "How far each planet sits north or south of the celestial equator. Planets at the same height act like a conjunction."
        ) {
            if let profile = store.activeProfile {
                ApproximateChartNote(profile: profile)
                LoadStateView(loader: loader, retry: { await reload() }) { data in
                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Declinations").font(.headline)
                            ForEach(data.declinations) { entry in
                                HStack {
                                    Text(entry.name)
                                    if entry.outOfBounds {
                                        Text("out of bounds")
                                            .font(.caption2.weight(.bold))
                                            .padding(.horizontal, 6)
                                            .padding(.vertical, 2)
                                            .background(Capsule().fill(Color.orange.opacity(0.25)))
                                    }
                                    Spacer()
                                    Text("\(String(format: "%.2f", entry.declination))°")
                                        .foregroundStyle(Color.textSecondary)
                                }
                                .font(.subheadline)
                                .accessibilityElement(children: .combine)
                            }
                        }
                    }
                    if !data.parallels.isEmpty {
                        CardView {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Parallels and contra-parallels").font(.headline)
                                ForEach(data.parallels) { parallel in
                                    HStack(alignment: .firstTextBaseline) {
                                        Text("\(parallel.planetA) \(parallel.type.replacingOccurrences(of: "_", with: " ")) \(parallel.planetB)")
                                        Spacer()
                                        Text("\(String(format: "%.2f", parallel.orb))° orb")
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                    .font(.subheadline)
                                    .accessibilityElement(children: .combine)
                                }
                            }
                        }
                    }
                    if let note = data.note, !note.isEmpty {
                        Text(note).font(.caption).foregroundStyle(Color.textSecondary)
                    }
                }
            } else {
                NeedsProfileCard()
            }
        }
        .task(id: String(describing: store.activeProfile?.id)) { await reload() }
    }

    private func reload() async {
        guard let profile = store.activeProfile else { return }
        await loader.load(.declinations(profile: profile))
    }
}

// MARK: - Fixed stars

struct FixedStarsView: View {
    @Environment(AppStore.self) private var store
    @State private var loader = AdvancedChartLoader<[FixedStarConjunction]>()
    @State private var prepareError: String?
    @State private var isPreparing = false

    var body: some View {
        AdvancedChartScaffold(
            eyebrow: "Chart",
            title: "Fixed Stars",
            subtitle: "Bright stars that sit within a degree of one of your planets. A close one is said to add its own flavour to that planet."
        ) {
            if let profile = store.activeProfile {
                ApproximateChartNote(profile: profile)
                if isPreparing || loader.isLoading {
                    ProgressView("Calculating…").tint(.white).frame(maxWidth: .infinity)
                } else if let message = prepareError ?? loader.error {
                    ErrorStateView(message: message) { await reload() }
                } else if let stars = loader.value {
                    if stars.isEmpty {
                        CardView {
                            Text("No bright fixed star sits within 1° of any of your planets.")
                                .font(.subtext)
                                .foregroundStyle(Color.textSecondary)
                        }
                    } else {
                        ForEach(stars) { star in
                            CardView {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("\(star.planet) with \(star.star)").font(.headline)
                                    Text("\(String(format: "%.2f", star.orb))° orb\(star.nature.isEmpty ? "" : " · \(star.nature)")")
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                    if !star.keywords.isEmpty {
                                        Text(star.keywords).font(.subheadline)
                                    }
                                    if !star.interpretation.isEmpty {
                                        Text(star.interpretation).font(.subtext).foregroundStyle(Color.textSecondary)
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                NeedsProfileCard()
            }
        }
        .task(id: String(describing: store.activeProfile?.id)) { await reload() }
    }

    @MainActor
    private func reload() async {
        guard let profile = store.activeProfile else { return }
        isPreparing = true
        prepareError = nil
        defer { isPreparing = false }
        do {
            // The star lookup works from planet longitudes, so get the birth chart first.
            let natal = try await DefaultChartRepository().natalChart(for: profile)
            let planets = natal.planets.compactMap { planet in
                planet.absoluteDegree.map { FixedStarPlanetInput(name: planet.name, absoluteDegree: $0) }
            }
            guard !planets.isEmpty else {
                prepareError = "Your birth chart has no planet positions to check yet."
                return
            }
            await loader.load(.fixedStars(planets: planets))
        } catch {
            prepareError = error.localizedDescription
        }
    }
}
