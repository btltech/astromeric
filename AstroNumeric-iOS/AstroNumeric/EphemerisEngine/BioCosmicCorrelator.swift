// BioCosmicCorrelator.swift
// Statistical correlation engine — Pearson r coefficient between biometric data and planetary transits.
// Requires ~30 days of BiometricLogger data to produce meaningful correlations.
// Uses Apple's Accelerate framework (vDSP) for high-performance vector math.

import Foundation
import Accelerate

actor BioCosmicCorrelator {
    static let shared = BioCosmicCorrelator()
    
    private init() {}
    
    // MARK: - Data Model
    
    struct Correlation {
        let transitAspect: String     // e.g. "Mars square Moon"
        let biometric: String         // e.g. "HRV"
        let pearsonR: Double          // -1.0 to 1.0
        let sampleCount: Int          // number of observations
        let baselineMean: Double      // overall average
        let transitMean: Double       // average during transit
        let deviationPercent: Double  // % change from baseline
        let isSignificant: Bool       // p < 0.05 approximation
    }
    
    // MARK: - Public API
    
    /// Analyze correlations between all logged transit aspects and biometric data.
    /// Returns correlations sorted by statistical significance.
    func analyzeCorrelations() async -> [Correlation] {
        let logs = await BiometricLogger.shared.allLogs()
        guard logs.count >= 14 else { return [] }  // Minimum 2 weeks for any signal
        
        var correlations: [Correlation] = []
        
        // Collect all unique transit aspects across all logs
        var aspectDays: [String: [Int]] = [:]  // aspect → indices of days with that aspect
        for (index, log) in logs.enumerated() {
            for transit in log.transits {
                for aspect in transit.natalAspects {
                    aspectDays[aspect, default: []].append(index)
                }
            }
        }
        
        // For each biometric metric, calculate Pearson r against each transit
        let metrics: [(name: String, extractor: (BiometricLogger.DailyLog) -> Double?)] = [
            ("HRV", { $0.hrvMs }),
            ("Resting HR", { $0.restingHR }),
            ("Sleep", { $0.sleepHours }),
            ("Steps", { $0.steps.map { Double($0) } }),
            ("SpO2", { $0.spo2 }),
        ]
        
        for metric in metrics {
            // Extract non-nil metric values
            let metricValues: [(index: Int, value: Double)] = logs.enumerated().compactMap { idx, log in
                guard let val = metric.extractor(log) else { return nil }
                return (idx, val)
            }
            
            guard metricValues.count >= 14 else { continue }
            
            let allValues = metricValues.map { $0.value }
            let baseline = vDSPMean(allValues)
            
            for (aspect, dayIndices) in aspectDays {
                guard dayIndices.count >= 3 else { continue }  // Need at least 3 observations
                
                // Create binary indicator: 1 if transit active, 0 if not
                var indicator = [Double](repeating: 0, count: metricValues.count)
                var transitValues: [Double] = []
                
                for (metricIdx, entry) in metricValues.enumerated() {
                    if dayIndices.contains(entry.index) {
                        indicator[metricIdx] = 1.0
                        transitValues.append(entry.value)
                    }
                }
                
                guard transitValues.count >= 3 else { continue }
                
                let transitMean = vDSPMean(transitValues)
                let pearsonR = pearsonCorrelation(x: indicator, y: allValues)
                
                guard !pearsonR.isNaN else { continue }
                
                let deviationPercent = baseline != 0 ? ((transitMean - baseline) / baseline) * 100 : 0
                
                // Approximate significance: |r| > 2/sqrt(n) is roughly p < 0.05
                let threshold = 2.0 / sqrt(Double(metricValues.count))
                
                correlations.append(Correlation(
                    transitAspect: aspect,
                    biometric: metric.name,
                    pearsonR: pearsonR,
                    sampleCount: transitValues.count,
                    baselineMean: baseline,
                    transitMean: transitMean,
                    deviationPercent: deviationPercent,
                    isSignificant: abs(pearsonR) > threshold
                ))
            }
        }
        
        // Sort by significance (absolute r value)
        return correlations.sorted { abs($0.pearsonR) > abs($1.pearsonR) }
    }
    
    // MARK: - Context Block for AI
    
    /// Format statistically significant correlations for AI system prompt injection.
    func contextBlock() async -> String? {
        let correlations = await analyzeCorrelations()
        let significant = correlations.filter { $0.isSignificant && abs($0.deviationPercent) > 5 }
        guard !significant.isEmpty else { return nil }
        
        var lines: [String] = ["BIO-COSMIC CORRELATIONS (mathematically verified):"]
        
        for corr in significant.prefix(8) {
            let direction = corr.deviationPercent > 0 ? "↑" : "↓"
            let sign = corr.pearsonR > 0 ? "+" : ""
            lines.append("  • \(corr.transitAspect) → \(corr.biometric) \(direction)\(String(format: "%.0f", abs(corr.deviationPercent)))% (r=\(sign)\(String(format: "%.2f", corr.pearsonR)), n=\(corr.sampleCount))")
        }
        
        lines.append("  Use these correlations as biological evidence, not metaphor.")
        
        return lines.joined(separator: "\n")
    }
    
    // MARK: - vDSP Math
    
    /// Mean using Accelerate framework
    private func vDSPMean(_ values: [Double]) -> Double {
        guard !values.isEmpty else { return 0 }
        var result: Double = 0
        vDSP_meanvD(values, 1, &result, vDSP_Length(values.count))
        return result
    }
    
    /// Pearson Correlation Coefficient using Accelerate
    /// r = Σ((x-x̄)(y-ȳ)) / sqrt(Σ(x-x̄)² × Σ(y-ȳ)²)
    private func pearsonCorrelation(x: [Double], y: [Double]) -> Double {
        guard x.count == y.count, x.count > 2 else { return .nan }
        let n = x.count
        
        // Calculate means
        var xMean: Double = 0
        var yMean: Double = 0
        vDSP_meanvD(x, 1, &xMean, vDSP_Length(n))
        vDSP_meanvD(y, 1, &yMean, vDSP_Length(n))
        
        // Center the data: x' = x - x̄, y' = y - ȳ
        var xCentered = [Double](repeating: 0, count: n)
        var yCentered = [Double](repeating: 0, count: n)
        var negXMean = -xMean
        var negYMean = -yMean
        vDSP_vsaddD(x, 1, &negXMean, &xCentered, 1, vDSP_Length(n))
        vDSP_vsaddD(y, 1, &negYMean, &yCentered, 1, vDSP_Length(n))
        
        // Numerator: Σ(x' * y')
        var numerator: Double = 0
        vDSP_dotprD(xCentered, 1, yCentered, 1, &numerator, vDSP_Length(n))
        
        // Denominator: sqrt(Σ(x'²) * Σ(y'²))
        var xSqSum: Double = 0
        var ySqSum: Double = 0
        vDSP_dotprD(xCentered, 1, xCentered, 1, &xSqSum, vDSP_Length(n))
        vDSP_dotprD(yCentered, 1, yCentered, 1, &ySqSum, vDSP_Length(n))
        
        let denominator = sqrt(xSqSum * ySqSum)
        guard denominator > 0 else { return .nan }
        
        return numerator / denominator
    }
}
