// HoraryJudge.swift
// Classical horary judgement for the Oracle, after William Lilly's Christian
// Astrology (1647): cast a chart for the moment and place of the question,
// find the planet for the person asking and the planet for the matter, and
// ask whether they come together. Every step is explained in plain words.

import Foundation

enum HoraryJudge {

    // MARK: - Tables

    static let signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    /// Traditional ruler of each sign, Aries first.
    static let rulers = [
        "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
        "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
    ]

    /// The sign (index) where each planet is exalted.
    static let exaltations: [String: Int] = [
        "Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6,
    ]

    enum Aspect: Double, CaseIterable {
        case conjunction = 0, sextile = 60, square = 90, trine = 120, opposition = 180

        var name: String {
            switch self {
            case .conjunction: return "conjunction"
            case .sextile: return "sextile"
            case .square: return "square"
            case .trine: return "trine"
            case .opposition: return "opposition"
            }
        }

        var plain: String {
            switch self {
            case .conjunction: return "a conjunction (meeting side by side)"
            case .sextile: return "a sextile (60°, an easy angle)"
            case .square: return "a square (90°, a hard angle)"
            case .trine: return "a trine (120°, the easiest angle)"
            case .opposition: return "an opposition (180°, face to face)"
            }
        }
    }

    /// An exact aspect between two planets, `days` from the chart's moment
    /// (negative for one that has already happened).
    struct Meeting: Equatable {
        let first: String
        let second: String
        let aspect: Aspect
        let days: Double
    }

    // MARK: - Aspect timing

    private static func normalized(_ degrees: Double) -> Double {
        let value = degrees.truncatingRemainder(dividingBy: 360)
        return value < 0 ? value + 360 : value
    }

    /// Days until the planet leaves its current sign (moving either way).
    static func daysLeftInSign(_ body: HoraryBody) -> Double {
        if body.speed > 0 { return (30 - body.degreeInSign) / body.speed }
        if body.speed < 0 { return body.degreeInSign / -body.speed }
        return .infinity
    }

    /// Days since the planet entered its current sign.
    static func daysInSign(_ body: HoraryBody) -> Double {
        if body.speed > 0 { return body.degreeInSign / body.speed }
        if body.speed < 0 { return (30 - body.degreeInSign) / -body.speed }
        return .infinity
    }

    /// Every exact aspect between `a` and `b`, as offsets in days, assuming
    /// each keeps its current speed: accurate over the days horary cares about.
    private static func aspectTimes(_ a: HoraryBody, _ b: HoraryBody) -> [(Aspect, Double, Double)] {
        let relativeSpeed = a.speed - b.speed
        guard abs(relativeSpeed) > 1e-6 else { return [] }
        let period = 360 / abs(relativeSpeed)
        let separation = normalized(a.longitude - b.longitude)
        var times: [(Aspect, Double, Double)] = []
        for aspect in Aspect.allCases {
            let targets = aspect == .conjunction || aspect == .opposition
                ? [aspect.rawValue]
                : [aspect.rawValue, 360 - aspect.rawValue]
            for target in targets {
                var next = ((target - separation) / relativeSpeed).truncatingRemainder(dividingBy: period)
                if next <= 1e-6 { next += period }
                let previous = next - period
                times.append((aspect, next, previous))
            }
        }
        return times
    }

    /// The next exact aspect between `a` and `b` before either leaves its sign.
    static func nextMeeting(_ a: HoraryBody, _ b: HoraryBody) -> Meeting? {
        let window = min(daysLeftInSign(a), daysLeftInSign(b))
        return aspectTimes(a, b)
            .filter { $0.1 <= window }
            .min { $0.1 < $1.1 }
            .map { Meeting(first: a.name, second: b.name, aspect: $0.0, days: $0.1) }
    }

    /// The last exact aspect between `a` and `b` since `a` entered its sign.
    static func lastMeeting(_ a: HoraryBody, _ b: HoraryBody) -> Meeting? {
        let window = daysInSign(a)
        return aspectTimes(a, b)
            .filter { -$0.2 <= window }
            .max { $0.2 < $1.2 }
            .map { Meeting(first: a.name, second: b.name, aspect: $0.0, days: $0.2) }
    }

    // MARK: - Dignity

    private static func isDomicile(_ planet: String, _ sign: Int) -> Bool { rulers[sign] == planet }
    private static func isExalted(_ planet: String, _ sign: Int) -> Bool { exaltations[planet] == sign }
    private static func isDetriment(_ planet: String, _ sign: Int) -> Bool { rulers[(sign + 6) % 12] == planet }
    private static func isFall(_ planet: String, _ sign: Int) -> Bool {
        guard let exalted = exaltations[planet] else { return false }
        return (exalted + 6) % 12 == sign
    }

    /// Whether `host` welcomes `guest`: the guest stands in a sign the host
    /// rules or is exalted in.
    private static func receives(_ host: String, _ guest: HoraryBody) -> Bool {
        isDomicile(host, guest.signIndex) || isExalted(host, guest.signIndex)
    }

    // MARK: - Wording

    /// "the Moon", "the Sun", "Venus".
    static func the(_ planet: String) -> String {
        planet == "Moon" || planet == "Sun" ? "the \(planet)" : planet
    }

    /// Sentence-start form: "The Moon", "Venus".
    static func The(_ planet: String) -> String {
        planet == "Moon" || planet == "Sun" ? "The \(planet)" : planet
    }

    // MARK: - Judgement

    private struct Point {
        let weight: Double
        let text: String
    }

    /// Judges `question` from `chart`. `speedAt` returns a planet's speed a
    /// number of days ahead, to spot a planet turning retrograde before it
    /// meets the other (refranation).
    static func judge(
        question: String,
        chart: HoraryChartData,
        speedAt: (String, Double) async -> Double?
    ) async -> HoraryReading {
        let topic = OracleTopic.detect(in: question)
        let bodies = Dictionary(chart.bodies.map { ($0.name, $0) }, uniquingKeysWith: { first, _ in first })
        guard let moon = bodies["Moon"] else {
            return HoraryReading(answer: "Wait", confidence: 0.5, reasoning: "The chart could not be calculated.", points: [], topic: topic, summary: "", voidOfCourse: false)
        }

        let ascSign = Int(chart.ascendant / 30) % 12
        let ascDegree = chart.ascendant.truncatingRemainder(dividingBy: 30)
        let querentName = rulers[ascSign]
        var points: [Point] = []

        // Who is who.
        let houseSign = Int(chart.cusps[topic.house - 1] / 30) % 12
        var quesitedName = rulers[houseSign]
        var sameRuler = false
        var intro = "At the moment you asked, \(signs[ascSign]) was rising, so \(the(querentName)) stands for you"
            + (querentName == "Moon" ? "." : ", with the Moon as your co-ruler.")
        switch topic {
        case .general:
            quesitedName = "Moon"
            intro += " With no specific topic, the answer rests on the Moon's next meeting with another planet."
        case .action:
            intro += " This is a question about your own plans (the 1st house), so the Moon's next contact with \(the(querentName)) decides it."
        default:
            intro += " Your question falls in \(topic.houseDescription), which begins in \(signs[houseSign]), so \(the(quesitedName)) stands for the matter."
            if quesitedName == querentName {
                sameRuler = true
                intro += " \(The(querentName)) rules both, so the Moon's contact with it decides."
            }
        }

        // Classical cautions before judgement.
        if ascDegree < 3 {
            points.append(Point(weight: -0.5, text: "The rising sign is only \(Int(ascDegree))° in: traditionally the question is premature, and things may still change."))
        } else if ascDegree >= 27 {
            points.append(Point(weight: -0.5, text: "The rising sign is at \(Int(ascDegree))°, near its end: traditionally much of this is already settled or out of your hands."))
        }
        if moon.longitude >= 195 && moon.longitude < 225 {
            points.append(Point(weight: -0.5, text: "The Moon is in the \"burnt path\" between mid-Libra and mid-Scorpio, a traditional warning of upset and unpredictability."))
        }

        // The Moon's next contact before leaving its sign; none means void of course.
        let moonNext = chart.bodies
            .filter { $0.name != "Moon" }
            .compactMap { nextMeeting(moon, $0) }
            .min { $0.days < $1.days }
        let voidOfCourse = moonNext == nil
        // Lilly: a void Moon still "performs" in Taurus, Cancer, Sagittarius and Pisces.
        let voidExempt = voidOfCourse && [1, 3, 8, 11].contains(moon.signIndex)
        let voidDenies = voidOfCourse && !voidExempt
        // "Should I…?" asks whether the matter is good for you; "Will…?" asks
        // whether it happens. Horary judges them differently.
        let advice = topic != .general && isAdviceQuestion(question)
        if advice {
            intro += " It's a \"should I\" question, so the Oracle weighs whether the matter is good for you, not only whether it happens."
        }

        // Find how the matter comes together, if it does.
        var meeting: Meeting?
        var via: String?
        if topic == .general {
            meeting = moonNext
        } else if topic == .action || sameRuler {
            if let querent = bodies[querentName], querentName != "Moon" {
                meeting = nextMeeting(moon, querent)
            } else {
                meeting = moonNext
            }
        } else if let querent = bodies[querentName], let quesited = bodies[quesitedName] {
            if querentName != quesitedName, let direct = nextMeeting(querent, quesited) {
                meeting = direct
            } else if quesitedName != "Moon", let lunar = nextMeeting(moon, quesited) {
                meeting = lunar
                via = "The Moon, your co-ruler,"
                // Translation of light: the Moon has just left you and heads
                // straight for the matter, carrying the connection between them.
                if querentName != "Moon", lastMeeting(moon, querent) != nil, moonNext?.second == quesitedName {
                    points.append(Point(weight: 0.5, text: "The Moon has just left \(the(querentName)) and heads straight for \(the(quesitedName)), carrying the connection between you and the matter (\"translation of light\"), often through a go-between."))
                }
            }
        }

        var answer: String
        var confidence: Double

        if let meeting {
            let timing = timingPhrase(days: meeting.days)
            let subject = via ?? The(meeting.first)
            let mover = bodies[meeting.first]
            let target = bodies[meeting.second]

            // Prohibition: a harsh contact from another planet gets there first.
            var prohibitor: String?
            for other in chart.bodies where other.name != meeting.first && other.name != meeting.second && other.name != "Moon" {
                for body in [mover, target].compactMap({ $0 }) {
                    if let early = nextMeeting(other, body), early.days < meeting.days,
                       [.conjunction, .square, .opposition].contains(early.aspect) {
                        prohibitor = other.name
                    }
                }
            }

            // Refranation: one of them turns retrograde before they meet.
            var refrains: String?
            for body in [mover, target].compactMap({ $0 }) where body.speed > 0 && body.name != "Sun" && body.name != "Moon" {
                if let later = await speedAt(body.name, meeting.days), later < 0 {
                    refrains = body.name
                }
            }

            let contact = "\(subject) is moving towards \(meeting.aspect.plain) with \(the(meeting.second)), \(timing)."
            if let refrains {
                points.append(Point(weight: -2, text: "\(contact) But \(the(refrains)) turns retrograde before they meet (\"refranation\"): one side backs out."))
                answer = "No"
                confidence = 0.68
            } else if let prohibitor {
                points.append(Point(weight: -2, text: "\(contact) But \(the(prohibitor)) reaches one of them first (\"prohibition\"): something or someone gets in the way."))
                answer = "No"
                confidence = 0.7
            } else if meeting.aspect == .opposition {
                points.append(Point(weight: 0.5, text: "\(contact) Meeting face to face still brings the matter about, but with conflict, and tradition warns it's often regretted."))
                answer = "Yes"
                confidence = 0.55
            } else if meeting.aspect == .square {
                points.append(Point(weight: 1.5, text: "\(contact) A square still brings the matter together, but with effort or delay."))
                answer = "Yes"
                confidence = 0.62
            } else {
                points.append(Point(weight: 2, text: "\(contact) In horary, that's the matter coming together."))
                answer = "Yes"
                confidence = 0.76
            }

            // General questions: the nature of the planet the Moon meets.
            if topic == .general, answer == "Yes" {
                if ["Mars", "Saturn"].contains(meeting.second) {
                    points.append(Point(weight: -1, text: "But the Moon's next contact is with \(the(meeting.second)), a traditionally harsh planet: expect friction."))
                    answer = meeting.aspect == .square ? "No" : "Yes"
                } else if ["Venus", "Jupiter"].contains(meeting.second) {
                    points.append(Point(weight: 1, text: "The Moon's next contact is with \(the(meeting.second)), a traditionally helpful planet."))
                    confidence += 0.05
                }
            }
        } else if voidDenies {
            points.append(Point(weight: advice ? -1 : -2, text: "The Moon is void of course: it makes no more contact with another planet before changing sign. Traditionally, little comes of the matter."))
            answer = "No"
            confidence = 0.8
        } else if advice {
            // Not happening yet isn't a verdict on whether it's good for you.
            answer = "No"
            confidence = 0.6
        } else {
            let pair = topic == .general || topic == .action || sameRuler
                ? "The Moon and \(the(querentName))"
                : "\(The(querentName)) and \(the(quesitedName))"
            points.append(Point(weight: -1.5, text: "\(pair) don't come together before one of them changes sign, so the chart doesn't show the matter happening."))
            answer = "No"
            confidence = 0.62
        }

        if voidExempt {
            points.append(Point(weight: 0.25, text: "The Moon is void of course, but in \(signs[moon.signIndex]), one of the four signs where Lilly said it still delivers."))
        }
        if voidDenies, meeting != nil, answer == "Yes" {
            points.append(Point(weight: -0.5, text: "The Moon is void of course, which weakens even a positive answer: results may be smaller than hoped."))
            confidence -= 0.08
        }

        // Testimonies about strength and goodwill.
        if let querent = bodies[querentName], let quesited = bodies[quesitedName], querentName != quesitedName {
            if receives(quesitedName, querent) {
                points.append(Point(weight: 0.5, text: "\(The(querentName)) sits in a sign ruled by \(the(quesitedName)): the matter welcomes you (\"reception\")."))
                confidence += 0.05
            }
            if receives(querentName, quesited) {
                points.append(Point(weight: 0.5, text: "\(The(quesitedName)) sits in a sign ruled by \(the(querentName)): you're well disposed towards it (\"reception\")."))
                confidence += 0.03
            }
        }
        for name in [querentName, quesitedName].enumerated().filter({ $0.offset == 0 || $0.element != querentName }).map(\.element) {
            guard let body = bodies[name], name != "Moon" || topic == .general else { continue }
            let role = name == querentName ? "you" : "the matter"
            if isDomicile(name, body.signIndex) || isExalted(name, body.signIndex) {
                points.append(Point(weight: 0.5, text: "\(The(name)), for \(role), is strong in \(signs[body.signIndex])."))
                confidence += 0.03
            } else if isDetriment(name, body.signIndex) || isFall(name, body.signIndex) {
                points.append(Point(weight: -0.5, text: "\(The(name)), for \(role), is weak in \(signs[body.signIndex])."))
                confidence -= 0.03
            }
            if body.speed < 0 {
                points.append(Point(weight: -0.5, text: "\(The(name)), for \(role), is retrograde: expect delays or second thoughts."))
                confidence -= 0.03
            }
            if name != "Sun", let sun = bodies["Sun"] {
                let distance = min(normalized(body.longitude - sun.longitude), normalized(sun.longitude - body.longitude))
                if distance < 8.5 {
                    points.append(Point(weight: -0.5, text: "\(The(name)), for \(role), is too close to the Sun (\"combust\"): weakened and hard to see clearly."))
                    confidence -= 0.03
                }
            }
        }

        let verdict: String
        if advice {
            // The Moon's next contact shows how things are likely to unfold.
            if let next = moonNext {
                let easy = [.conjunction, .sextile, .trine].contains(next.aspect)
                let helpful = ["Venus", "Jupiter"].contains(next.second)
                let harsh = ["Mars", "Saturn"].contains(next.second)
                let how = "\(next.aspect.plain) with \(the(next.second)), \(timingPhrase(days: next.days))"
                if easy && !harsh {
                    points.append(Point(weight: helpful ? 1.5 : 1, text: "The Moon, which shows how events unfold, next makes \(how): things are likely to go smoothly."))
                } else if !easy && harsh {
                    points.append(Point(weight: -1.5, text: "The Moon, which shows how events unfold, next makes \(how), a traditionally harsh planet: expect friction."))
                } else if easy {
                    points.append(Point(weight: 0.5, text: "The Moon next makes \(how): workable, though \(the(next.second)) asks for patience."))
                } else {
                    points.append(Point(weight: helpful ? 0.5 : -1, text: "The Moon next makes \(how): some tension along the way."))
                }
            }
            let score = points.reduce(0) { $0 + $1.weight }
            answer = score > 0 ? "Yes" : (score < 0 ? "No" : "Wait")
            confidence = answer == "Wait" ? 0.5 : 0.55 + 0.06 * abs(score)
            switch answer {
            case "Yes": verdict = "Weighing the chart, the signs favour it, so the answer is yes."
            case "No": verdict = "Weighing the chart, the signs lean against it, so the answer is no for now."
            default: verdict = "The signs for and against are evenly balanced, so the Oracle says wait."
            }
        } else {
            switch answer {
            case "Yes": verdict = "The chart shows the matter coming together, so the answer is yes."
            default: verdict = "The chart doesn't show the matter coming together, so the answer is no for now."
            }
        }
        confidence = min(0.9, max(0.5, confidence))

        let summary = "\(signs[ascSign]) \(Int(ascDegree))° rising | You: \(querentName)"
            + (topic == .general || topic == .action ? "" : " | \(topic.houseOrdinal) house: \(quesitedName)")
            + " | Moon \(Int(moon.degreeInSign))° \(signs[moon.signIndex])"
            + (voidOfCourse ? " (void)" : "")

        return HoraryReading(
            answer: answer,
            confidence: confidence,
            reasoning: "\(intro) \(verdict)",
            points: points
                .sorted { abs($0.weight) > abs($1.weight) }
                .map { OracleFactorLine(helps: $0.weight > 0, text: $0.text) },
            topic: topic,
            summary: summary,
            voidOfCourse: voidOfCourse
        )
    }

    /// "Should I…?", "Is it wise to…?" and similar ask for advice.
    static func isAdviceQuestion(_ question: String) -> Bool {
        let q = question.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        let openers = ["should", "shall", "ought", "is it wise", "is it a good idea", "is it worth",
                       "would it be good", "would it be wise", "is now a good time", "is this a good time"]
        return openers.contains { q.hasPrefix($0) }
    }

    private static func timingPhrase(days: Double) -> String {
        let hours = days * 24
        if hours < 1 { return "within the hour" }
        if hours < 36 {
            let rounded = Int(hours.rounded())
            return "exact in about \(rounded) hour\(rounded == 1 ? "" : "s")"
        }
        if days < 14 { return "exact in about \(Int(days.rounded())) days" }
        return "exact in about \(Int((days / 7).rounded())) weeks"
    }
}

/// The judge's verdict, before it becomes a `YesNoAnswer`.
struct HoraryReading {
    let answer: String
    let confidence: Double
    let reasoning: String
    let points: [OracleFactorLine]
    let topic: OracleTopic
    /// A one-line chart summary for the "Sky when you asked" box.
    let summary: String
    let voidOfCourse: Bool
}
