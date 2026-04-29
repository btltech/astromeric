// CosmicBackgroundView.swift
// SwiftUI wrapper for SpriteKit cosmic scene with lifecycle + accessibility

import SwiftUI
import SpriteKit

private final class NonFocusableSKView: SKView {
    override var canBecomeFocused: Bool { false }
}

struct CosmicBackgroundView: UIViewRepresentable {
    /// Element for tinting (Fire, Water, Air, Earth)
    let element: String?
    
    /// Scene phase for lifecycle management
    @Environment(\.scenePhase) private var scenePhase
    
    func makeUIView(context: Context) -> SKView {
        let view = NonFocusableSKView()
        view.ignoresSiblingOrder = true
        view.allowsTransparency = true
        view.preferredFramesPerSecond = 30 // Battery savings
        view.showsFPS = false
        view.showsNodeCount = false
        
        // This view is purely decorative; don't participate in focus/navigation.
        view.isUserInteractionEnabled = false
        view.accessibilityElementsHidden = true
        
        // Check for reduced motion preference
        if UIAccessibility.isReduceMotionEnabled {
            // Static background only
            view.backgroundColor = UIColor(red: 0.04, green: 0.05, blue: 0.08, alpha: 1)
            return view
        }
        
        // Use the active window scene's bounds (replaces deprecated UIScreen.main).
        // Falls back to a sensible default; updateUIView resizes on first layout.
        let initialSize: CGSize = {
            if let scene = UIApplication.shared.connectedScenes
                .compactMap({ $0 as? UIWindowScene })
                .first(where: { $0.activationState == .foregroundActive })
                ?? UIApplication.shared.connectedScenes
                    .compactMap({ $0 as? UIWindowScene })
                    .first {
                return scene.screen.bounds.size
            }
            return CGSize(width: 390, height: 844)
        }()
        let scene = CosmicScene(size: initialSize)
        scene.scaleMode = .resizeFill
        view.presentScene(scene)

        return view
    }
    
    func updateUIView(_ uiView: SKView, context: Context) {
        guard let scene = uiView.scene as? CosmicScene else { return }
        
        // Lifecycle management - pause when backgrounded
        switch scenePhase {
        case .active:
            scene.isPaused = false
        case .inactive, .background:
            scene.isPaused = true
        @unknown default:
            break
        }
        
        // Handle resize for rotation, split screen, etc.
        let newSize = uiView.bounds.size
        if scene.size != newSize && newSize.width > 0 && newSize.height > 0 {
            scene.resize(to: newSize)
        }
        
        // Update element tint
        scene.updateForElement(element)
    }
}

// MARK: - View Extension for Hit Testing

extension View {
    /// Applies cosmic background with proper settings
    func cosmicBackground(element: String? = nil) -> some View {
        self.background {
            CosmicBackgroundView(element: element)
                .ignoresSafeArea()
                .allowsHitTesting(false)
                .accessibilityHidden(true) // Decorative element
        }
    }
}

// MARK: - Preview

#Preview {
    ZStack {
        CosmicBackgroundView(element: "Fire")
            .ignoresSafeArea()
            .allowsHitTesting(false)
        
        VStack {
            Text("ui.cosmicBackground.0".localized)
                .font(.largeTitle.bold())
                .foregroundStyle(.white)
        }
    }
    .preferredColorScheme(.dark)
}
