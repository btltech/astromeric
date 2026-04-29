import Foundation

enum PrivacyDisplayRole {
    case activeUser
    case genericProfile
    case partner
    case friend
    case share
}

enum PrivacyRedaction {
    static let maskedDate = "••••-••-••"
    static let hiddenValue = "Hidden"
    static let privateUser = "Private User"
    static let privateProfile = "Private Profile"
    static let partnerLabel = "Other Person"
    static let friendLabel = "Friend"
}

extension Profile {
    func displayName(
        hideSensitive: Bool,
        role: PrivacyDisplayRole = .genericProfile,
        index: Int? = nil
    ) -> String {
        guard hideSensitive else { return name }

        switch role {
        case .activeUser:
            return "You"
        case .partner:
            return PrivacyRedaction.partnerLabel
        case .friend:
            return PrivacyRedaction.friendLabel
        case .share:
            return PrivacyRedaction.privateProfile
        case .genericProfile:
            if let index {
                return "Profile \(index + 1)"
            }
            let normalizedId = abs(id)
            return normalizedId > 0 ? "Profile \(normalizedId)" : PrivacyRedaction.privateProfile
        }
    }

    func maskedDateOfBirth(hideSensitive: Bool) -> String {
        hideSensitive ? PrivacyRedaction.maskedDate : dateOfBirth
    }

    func maskedBirthTime(hideSensitive: Bool) -> String {
        guard let timeOfBirth, !timeOfBirth.isEmpty else { return "Not set" }
        return hideSensitive ? PrivacyRedaction.hiddenValue : timeOfBirth
    }

    func maskedBirthplace(hideSensitive: Bool) -> String {
        guard let placeOfBirth, !placeOfBirth.isEmpty else { return "Not set" }
        return hideSensitive ? PrivacyRedaction.hiddenValue : placeOfBirth
    }

    func promptName(hideSensitive: Bool) -> String {
        hideSensitive ? PrivacyRedaction.privateUser : name
    }

    func promptBirthDate(hideSensitive: Bool) -> String {
        hideSensitive ? "Hidden for privacy" : dateOfBirth
    }

    func promptBirthTime(hideSensitive: Bool) -> String {
        guard let timeOfBirth, !timeOfBirth.isEmpty else { return "unknown" }
        return hideSensitive ? "Hidden for privacy" : timeOfBirth
    }

    func promptBirthPlace(hideSensitive: Bool) -> String {
        guard let placeOfBirth, !placeOfBirth.isEmpty else { return "unknown" }
        return hideSensitive ? "Hidden for privacy" : placeOfBirth
    }

    func privacySafePayload(hideSensitive: Bool) -> ProfilePayload {
        ProfilePayload(
            name: hideSensitive ? PrivacyRedaction.privateUser : name,
            dateOfBirth: dateOfBirth,
            timeOfBirth: timeOfBirth,
            placeOfBirth: hideSensitive ? nil : placeOfBirth,
            latitude: latitude,
            longitude: longitude,
            timezone: timezone,
            houseSystem: houseSystem
        )
    }
}

extension SavedRelationship {
    func displayPair(hideSensitive: Bool) -> String {
        hideSensitive ? "\(type.displayName) Match" : "\(personAName) & \(personBName)"
    }

    func displayPersonAName(hideSensitive: Bool) -> String {
        hideSensitive ? "You" : personAName
    }

    func displayPersonBName(hideSensitive: Bool) -> String {
        hideSensitive ? "\(type.displayName) Match" : personBName
    }

    func displayPersonADOB(hideSensitive: Bool) -> String {
        hideSensitive ? PrivacyRedaction.maskedDate : personADOB
    }

    func displayPersonBDOB(hideSensitive: Bool) -> String {
        hideSensitive ? PrivacyRedaction.maskedDate : personBDOB
    }

    func redactedCopy() -> SavedRelationship {
        SavedRelationship(
            id: id,
            personAName: "You",
            personBName: "\(type.displayName) Match",
            personADOB: PrivacyRedaction.maskedDate,
            personBDOB: PrivacyRedaction.maskedDate,
            type: type,
            overallScore: overallScore,
            categories: categories,
            strengths: strengths,
            challenges: challenges,
            createdAt: createdAt,
            lastUpdated: lastUpdated
        )
    }
}

extension FriendCompatibility {
    func displayName(hideSensitive: Bool) -> String {
        hideSensitive ? "\(relationshipType.capitalized) Match" : friendName
    }
}
