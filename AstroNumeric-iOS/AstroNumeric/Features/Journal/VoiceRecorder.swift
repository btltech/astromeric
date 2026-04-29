// VoiceRecorder.swift
// Live speech-to-text for voice journaling using SFSpeechRecognizer.
// Appends transcribed text to a binding in real-time.

import Foundation
import Speech
import AVFoundation
import Observation

@Observable
final class VoiceRecorder {
    // MARK: - State
    
    /// Whether currently recording
    private(set) var isRecording = false
    
    /// Live transcript of current session
    private(set) var transcript = ""
    
    /// Error message
    var error: String?
    
    /// Authorization status
    private(set) var isAuthorized = false
    
    // MARK: - Private
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    
    // MARK: - Authorization
    
    /// Request both speech recognition and microphone permissions.
    func requestAuthorization() async {
        // Speech recognition permission
        let speechStatus = await withCheckedContinuation { continuation in
            SFSpeechRecognizer.requestAuthorization { status in
                continuation.resume(returning: status)
            }
        }
        
        guard speechStatus == .authorized else {
            await MainActor.run { error = "Speech recognition not authorized" }
            return
        }
        
        // Microphone permission
        let micGranted: Bool
        if #available(iOS 17.0, *) {
            micGranted = await AVAudioApplication.requestRecordPermission()
        } else {
            micGranted = await withCheckedContinuation { continuation in
                AVAudioSession.sharedInstance().requestRecordPermission { granted in
                    continuation.resume(returning: granted)
                }
            }
        }
        
        guard micGranted else {
            await MainActor.run { error = "Microphone access not authorized" }
            return
        }
        
        await MainActor.run { isAuthorized = true }
    }
    
    // MARK: - Recording
    
    /// Start recording and transcribing speech.
    @MainActor
    func startRecording() {
        guard !isRecording else { return }
        guard speechRecognizer?.isAvailable == true else {
            error = "Speech recognition unavailable"
            return
        }
        
        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            self.error = "Audio session error: \(error.localizedDescription)"
            return
        }
        
        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let request = recognitionRequest else { return }
        request.shouldReportPartialResults = true
        
        // On-device recognition if available (privacy + offline)
        if #available(iOS 13, *), speechRecognizer?.supportsOnDeviceRecognition == true {
            request.requiresOnDeviceRecognition = true
        }
        
        // Start recognition task
        recognitionTask = speechRecognizer?.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }
            
            if let result = result {
                Task { @MainActor in
                    self.transcript = result.bestTranscription.formattedString
                }
            }
            
            if error != nil || (result?.isFinal ?? false) {
                Task { @MainActor in
                    self.stopRecordingInternal()
                }
            }
        }
        
        // Install audio tap
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, _ in
            self?.recognitionRequest?.append(buffer)
        }
        
        do {
            audioEngine.prepare()
            try audioEngine.start()
            isRecording = true
            transcript = ""
        } catch {
            self.error = "Audio engine error: \(error.localizedDescription)"
        }
    }
    
    /// Stop recording and finalize transcription.
    @MainActor
    func stopRecording() -> String {
        let finalText = transcript
        stopRecordingInternal()
        return finalText
    }
    
    /// Toggle recording state.
    @MainActor
    func toggle() -> String? {
        if isRecording {
            return stopRecording()
        } else {
            startRecording()
            return nil
        }
    }
    
    // MARK: - Private
    
    @MainActor
    private func stopRecordingInternal() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionRequest = nil
        recognitionTask?.cancel()
        recognitionTask = nil
        isRecording = false
        
        try? AVAudioSession.sharedInstance().setActive(false)
    }
}
