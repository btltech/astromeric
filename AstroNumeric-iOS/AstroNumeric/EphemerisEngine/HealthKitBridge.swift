// HealthKitBridge.swift
// Cosmic biometric data collection — reads health metrics and correlates with astrological transits.
// Collects optional sleep, heart rate, HRV, steps, energy, and mindfulness context.

import Foundation
import HealthKit

actor HealthKitBridge {
    static let shared = HealthKitBridge()
    
    private let store = HKHealthStore()
    private var isAuthorized = false
    
    // MARK: - Health Data Types
    
    /// All data types we want to read
    private var readTypes: Set<HKObjectType> {
        Set([
            HKQuantityType.quantityType(forIdentifier: .heartRate)!,
            HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
            HKQuantityType.quantityType(forIdentifier: .restingHeartRate)!,
            HKQuantityType.quantityType(forIdentifier: .stepCount)!,
            HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned)!,
            HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning)!,
            HKQuantityType.quantityType(forIdentifier: .oxygenSaturation)!,
            HKQuantityType.quantityType(forIdentifier: .respiratoryRate)!,
            HKCategoryType.categoryType(forIdentifier: .sleepAnalysis)!,
            HKCategoryType.categoryType(forIdentifier: .mindfulSession)!,
        ])
    }
    
    // MARK: - Authorization
    
    /// Check if HealthKit is available on this device
    var isAvailable: Bool {
        HKHealthStore.isHealthDataAvailable()
    }
    
    /// Request authorization to read health data. Silent no-op if already authorized or unavailable.
    func requestAuthorization() async -> Bool {
        guard isAvailable else {
            DebugLog.log("HealthKit: not available on this device")
            return false
        }
        guard !isAuthorized else { return true }
        
        do {
            // Read-only access (we never write health data)
            try await store.requestAuthorization(toShare: [], read: readTypes)
            isAuthorized = true
            DebugLog.log("HealthKit: authorization granted")
            return true
        } catch {
            DebugLog.log("HealthKit: authorization failed — \(error)")
            return false
        }
    }
    
    // MARK: - Data Collection
    
    /// Collect a snapshot of today's biometrics.
    /// Returns a `BiometricSnapshot` with all available metrics.
    func collectTodaySnapshot() async -> BiometricSnapshot {
        guard isAuthorized else { return BiometricSnapshot() }
        
        let calendar = Calendar.current
        let now = Date()
        let startOfDay = calendar.startOfDay(for: now)
        let yesterday = calendar.date(byAdding: .day, value: -1, to: startOfDay)!
        
        let bpmUnit = HKUnit.count().unitDivided(by: .minute())
        
        async let heartRate = latestQuantity(.heartRate, unit: bpmUnit)
        async let restingHR = latestQuantity(.restingHeartRate, unit: bpmUnit)
        async let hrv = latestQuantity(.heartRateVariabilitySDNN, unit: .secondUnit(with: .milli))
        async let steps = sumQuantity(.stepCount, unit: .count(), from: startOfDay, to: now)
        async let activeEnergy = sumQuantity(.activeEnergyBurned, unit: .kilocalorie(), from: startOfDay, to: now)
        async let distance = sumQuantity(.distanceWalkingRunning, unit: .mile(), from: startOfDay, to: now)
        async let spo2 = latestQuantity(.oxygenSaturation, unit: .percent())
        async let respiratoryRate = latestQuantity(.respiratoryRate, unit: bpmUnit)
        async let sleepHours = sleepDuration(from: yesterday, to: now)
        async let mindfulMinutes = mindfulDuration(from: startOfDay, to: now)
        
        return BiometricSnapshot(
            heartRate: await heartRate,
            restingHeartRate: await restingHR,
            hrvMs: await hrv,
            steps: await steps.map { Int($0) },
            activeCalories: await activeEnergy,
            distanceMiles: await distance,
            spo2Percent: await spo2.map { $0 * 100 }, // convert from 0-1 to 0-100
            respiratoryRate: await respiratoryRate,
            sleepHours: await sleepHours,
            mindfulMinutes: await mindfulMinutes,
            timestamp: now
        )
    }
    
    // MARK: - Private Query Helpers
    
    /// Get the most recent sample value for a quantity type.
    private func latestQuantity(_ identifier: HKQuantityTypeIdentifier, unit: HKUnit) async -> Double? {
        guard let type = HKQuantityType.quantityType(forIdentifier: identifier) else { return nil }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: Calendar.current.date(byAdding: .day, value: -1, to: Date()),
            end: Date(),
            options: .strictStartDate
        )
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
        
        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: 1,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                if let sample = samples?.first as? HKQuantitySample {
                    continuation.resume(returning: sample.quantity.doubleValue(for: unit))
                } else {
                    continuation.resume(returning: nil)
                }
            }
            store.execute(query)
        }
    }
    
    /// Get the sum of a quantity type over a date range.
    private func sumQuantity(_ identifier: HKQuantityTypeIdentifier, unit: HKUnit, from start: Date, to end: Date) async -> Double? {
        guard let type = HKQuantityType.quantityType(forIdentifier: identifier) else { return nil }
        
        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: .strictStartDate)
        
        return await withCheckedContinuation { continuation in
            let query = HKStatisticsQuery(
                quantityType: type,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum
            ) { _, result, error in
                if let sum = result?.sumQuantity() {
                    continuation.resume(returning: sum.doubleValue(for: unit))
                } else {
                    continuation.resume(returning: nil)
                }
            }
            store.execute(query)
        }
    }
    
    /// Calculate total mindful session duration from category samples.
    private func mindfulDuration(from start: Date, to end: Date) async -> Double? {
        guard let type = HKCategoryType.categoryType(forIdentifier: .mindfulSession) else { return nil }
        
        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: .strictStartDate)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)
        
        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                guard let sessions = samples as? [HKCategorySample] else {
                    continuation.resume(returning: nil)
                    return
                }
                let totalMinutes = sessions.reduce(0.0) {
                    $0 + $1.endDate.timeIntervalSince($1.startDate) / 60.0
                }
                continuation.resume(returning: totalMinutes > 0 ? totalMinutes : nil)
            }
            store.execute(query)
        }
    }
    
    /// Calculate total sleep duration from sleep analysis samples.
    private func sleepDuration(from start: Date, to end: Date) async -> Double? {
        guard let type = HKCategoryType.categoryType(forIdentifier: .sleepAnalysis) else { return nil }
        
        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: .strictStartDate)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)
        
        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                guard let sleepSamples = samples as? [HKCategorySample] else {
                    continuation.resume(returning: nil)
                    return
                }
                
                // Sum only "asleep" categories (not "in bed")
                let asleepValues: Set<Int> = [
                    HKCategoryValueSleepAnalysis.asleepCore.rawValue,
                    HKCategoryValueSleepAnalysis.asleepDeep.rawValue,
                    HKCategoryValueSleepAnalysis.asleepREM.rawValue,
                    HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue,
                ]
                
                let totalSeconds = sleepSamples
                    .filter { asleepValues.contains($0.value) }
                    .reduce(0.0) { $0 + $1.endDate.timeIntervalSince($1.startDate) }
                
                let hours = totalSeconds / 3600.0
                continuation.resume(returning: hours > 0 ? hours : nil)
            }
            store.execute(query)
        }
    }
}

// MARK: - Biometric Snapshot

struct BiometricSnapshot: Codable {
    var heartRate: Double?
    var restingHeartRate: Double?
    var hrvMs: Double?
    var steps: Int?
    var activeCalories: Double?
    var distanceMiles: Double?
    var spo2Percent: Double?
    var respiratoryRate: Double?
    var sleepHours: Double?
    var mindfulMinutes: Double?
    var timestamp: Date?
    
    /// Format as a text block for AI system prompt injection
    var promptDescription: String {
        var lines: [String] = []
        if let hr = heartRate { lines.append("  - Heart Rate: \(Int(hr)) bpm") }
        if let rhr = restingHeartRate { lines.append("  - Resting HR: \(Int(rhr)) bpm") }
        if let hrv = hrvMs { lines.append("  - HRV: \(String(format: "%.0f", hrv)) ms") }
        if let s = steps { lines.append("  - Steps: \(s)") }
        if let cal = activeCalories { lines.append("  - Active Calories: \(Int(cal)) kcal") }
        if let dist = distanceMiles { lines.append("  - Distance: \(String(format: "%.1f", dist)) mi") }
        if let spo2 = spo2Percent { lines.append("  - SpO2: \(String(format: "%.0f", spo2))%") }
        if let rr = respiratoryRate { lines.append("  - Respiratory Rate: \(String(format: "%.0f", rr))/min") }
        if let sleep = sleepHours { lines.append("  - Sleep: \(String(format: "%.1f", sleep)) hrs") }
        if let mindful = mindfulMinutes { lines.append("  - Mindful Minutes: \(Int(mindful))") }
        return lines.isEmpty ? "  - No biometric data available" : lines.joined(separator: "\n")
    }
    
    /// Whether any data was collected
    var hasData: Bool {
        heartRate != nil || restingHeartRate != nil || hrvMs != nil ||
        steps != nil || activeCalories != nil || sleepHours != nil
    }
}
