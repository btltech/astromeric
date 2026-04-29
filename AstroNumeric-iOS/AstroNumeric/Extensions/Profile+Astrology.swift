// Profile+Astrology.swift
// Zodiac calculation logic extracted from views

import Foundation

extension Profile {
    
    /// Calculate the sun sign from the profile's date of birth
    var sunSign: String {
        guard let monthDay = parseBirthDateMonthDay() else {
            return "Aquarius" // Default fallback
        }
        
        let (month, day) = monthDay
        
        switch (month, day) {
        case (3, 21...31), (4, 1...19): return "Aries"
        case (4, 20...30), (5, 1...20): return "Taurus"
        case (5, 21...31), (6, 1...20): return "Gemini"
        case (6, 21...30), (7, 1...22): return "Cancer"
        case (7, 23...31), (8, 1...22): return "Leo"
        case (8, 23...31), (9, 1...22): return "Virgo"
        case (9, 23...30), (10, 1...22): return "Libra"
        case (10, 23...31), (11, 1...21): return "Scorpio"
        case (11, 22...30), (12, 1...21): return "Sagittarius"
        case (12, 22...31), (1, 1...19): return "Capricorn"
        case (1, 20...31), (2, 1...18): return "Aquarius"
        case (2, 19...29), (3, 1...20): return "Pisces"
        default: return "Aquarius"
        }
    }
    
    /// Emoji representation of the sun sign
    var sunSignEmoji: String {
        switch sunSign {
        case "Aries": return "♈️"
        case "Taurus": return "♉️"
        case "Gemini": return "♊️"
        case "Cancer": return "♋️"
        case "Leo": return "♌️"
        case "Virgo": return "♍️"
        case "Libra": return "♎️"
        case "Scorpio": return "♏️"
        case "Sagittarius": return "♐️"
        case "Capricorn": return "♑️"
        case "Aquarius": return "♒️"
        case "Pisces": return "♓️"
        default: return "⭐️"
        }
    }
    
    /// Element of the sun sign (Fire, Earth, Air, Water)
    var element: String {
        switch sunSign {
        case "Aries", "Leo", "Sagittarius": return "Fire"
        case "Taurus", "Virgo", "Capricorn": return "Earth"
        case "Gemini", "Libra", "Aquarius": return "Air"
        case "Cancer", "Scorpio", "Pisces": return "Water"
        default: return "Air"
        }
    }
    
    /// Modality of the sun sign (Cardinal, Fixed, Mutable)
    var modality: String {
        switch sunSign {
        case "Aries", "Cancer", "Libra", "Capricorn": return "Cardinal"
        case "Taurus", "Leo", "Scorpio", "Aquarius": return "Fixed"
        case "Gemini", "Virgo", "Sagittarius", "Pisces": return "Mutable"
        default: return "Fixed"
        }
    }
    
    /// Alias for sunSign (used by ChatContext and legacy code)
    var sign: String? {
        sunSign
    }

    /// Local life path calculation for light-weight UI surfaces such as share cards.
    /// Matches the app's documented numerology systems:
    /// - Pythagorean reduces month/day/year separately before the final reduction
    /// - Chaldean sums all DOB digits directly
    func lifePathNumber(useChaldean: Bool = false) -> Int? {
        let components = dateOfBirth.split(separator: "-")
        guard components.count == 3,
              let year = Int(components[0]),
              let month = Int(components[1]),
              let day = Int(components[2]) else {
            return nil
        }

        if useChaldean {
            return Self.reduceNumerologyNumber(
                Self.sumDigits(year) + Self.sumDigits(month) + Self.sumDigits(day),
                keepMasterNumbers: true
            )
        }

        let reducedYear = Self.reduceNumerologyNumber(year, keepMasterNumbers: true)
        let reducedMonth = Self.reduceNumerologyNumber(month, keepMasterNumbers: true)
        let reducedDay = Self.reduceNumerologyNumber(day, keepMasterNumbers: true)
        return Self.reduceNumerologyNumber(reducedYear + reducedMonth + reducedDay, keepMasterNumbers: true)
    }
    
    // MARK: - Private Helpers
    
    private func parseBirthDateMonthDay() -> (Int, Int)? {
        // Expected format: "YYYY-MM-DD"
        let components = dateOfBirth.split(separator: "-")
        guard components.count == 3,
              let month = Int(components[1]),
              let day = Int(components[2]) else {
            return nil
        }
        return (month, day)
    }

    private static func sumDigits(_ number: Int) -> Int {
        String(abs(number)).compactMap { Int(String($0)) }.reduce(0, +)
    }

    private static func reduceNumerologyNumber(_ number: Int, keepMasterNumbers: Bool) -> Int {
        var current = abs(number)
        let masters: Set<Int> = keepMasterNumbers ? [11, 22, 33] : []

        while current > 9, !masters.contains(current) {
            current = sumDigits(current)
        }

        return current
    }
}
