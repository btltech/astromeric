// CosmicScene.swift
// Premium SpriteKit starfield background with signature cosmic identity

import SpriteKit

final class CosmicScene: SKScene {
    
    // MARK: - Properties
    
    private var backgroundStars: SKEmitterNode?
    private var twinklingStars: SKEmitterNode?
    private var shootingStarTimer: Timer?
    private var nebulaNodes: [SKSpriteNode] = []
    private var currentElement: String?
    
    // Multiple gradient layers for depth
    private var gradientLayer1: SKSpriteNode?
    private var gradientLayer2: SKSpriteNode?
    
    // MARK: - Lifecycle
    
    override func didMove(to view: SKView) {
        backgroundColor = UIColor(red: 0.02, green: 0.02, blue: 0.06, alpha: 1)
        
        setupMultiLayerGradient()
        setupBackgroundStars()
        setupTwinklingStars()
        setupShootingStars()
    }
    
    override func willMove(from view: SKView) {
        shootingStarTimer?.invalidate()
        shootingStarTimer = nil
    }
    
    override var isPaused: Bool {
        didSet {
            if isPaused {
                shootingStarTimer?.invalidate()
                shootingStarTimer = nil
            } else if shootingStarTimer == nil {
                scheduleNextShootingStar()
            }
        }
    }
    
    // MARK: - Public API
    
    func resize(to newSize: CGSize) {
        guard newSize.width > 0, newSize.height > 0 else { return }
        
        size = newSize
        let center = CGPoint(x: newSize.width / 2, y: newSize.height / 2)
        
        // Update star emitters
        backgroundStars?.position = center
        backgroundStars?.particlePositionRange = CGVector(dx: newSize.width * 1.3, dy: newSize.height * 1.3)
        
        twinklingStars?.position = center
        twinklingStars?.particlePositionRange = CGVector(dx: newSize.width * 1.2, dy: newSize.height * 1.2)
        
        // Update gradient layers
        gradientLayer1?.position = center
        gradientLayer1?.size = newSize
        gradientLayer2?.position = CGPoint(x: newSize.width * 0.7, y: newSize.height * 0.3)
        gradientLayer2?.size = CGSize(width: newSize.width * 0.8, height: newSize.height * 0.6)
    }
    
    func updateForElement(_ element: String?) {
        guard element != currentElement else { return }
        currentElement = element
        
        let primaryColor: SKColor
        let secondaryColor: SKColor
        
        switch element {
        case "Fire":
            primaryColor = SKColor(red: 1.0, green: 0.3, blue: 0.2, alpha: 0.4)
            secondaryColor = SKColor(red: 1.0, green: 0.6, blue: 0.0, alpha: 0.3)
        case "Water":
            primaryColor = SKColor(red: 0.2, green: 0.4, blue: 1.0, alpha: 0.4)
            secondaryColor = SKColor(red: 0.1, green: 0.8, blue: 0.9, alpha: 0.3)
        case "Air":
            primaryColor = SKColor(red: 0.5, green: 0.8, blue: 1.0, alpha: 0.4)
            secondaryColor = SKColor(red: 0.9, green: 0.9, blue: 1.0, alpha: 0.3)
        case "Earth":
            primaryColor = SKColor(red: 0.3, green: 0.7, blue: 0.3, alpha: 0.4)
            secondaryColor = SKColor(red: 0.6, green: 0.5, blue: 0.3, alpha: 0.3)
        default:
            // Default signature purple/violet cosmic palette
            primaryColor = SKColor(red: 0.5, green: 0.3, blue: 0.9, alpha: 0.4)
            secondaryColor = SKColor(red: 0.8, green: 0.4, blue: 0.7, alpha: 0.3)
        }
        
        // Animate gradient transition
        let fadeOut = SKAction.fadeAlpha(to: 0.1, duration: 0.3)
        let fadeIn = SKAction.fadeAlpha(to: 0.35, duration: 0.3)
        let sequence = SKAction.sequence([fadeOut, fadeIn])
        
        gradientLayer1?.run(sequence)
        gradientLayer2?.run(sequence)
        
        // Update star colors with smooth transition
        let colorAction = SKAction.customAction(withDuration: 0.5) { [weak self] _, _ in
            self?.twinklingStars?.particleColor = primaryColor.withAlphaComponent(0.8)
            self?.backgroundStars?.particleColor = secondaryColor.withAlphaComponent(0.5)
        }
        twinklingStars?.run(colorAction)
    }
    
    // MARK: - Multi-Layer Gradient Setup
    
    private func setupMultiLayerGradient() {
        // Primary gradient (center, larger)
        let gradient1 = createGradientSprite(
            colors: [
                UIColor(red: 0.4, green: 0.2, blue: 0.8, alpha: 0.5),
                UIColor(red: 0.2, green: 0.1, blue: 0.4, alpha: 0.2),
                UIColor.clear
            ],
            size: size
        )
        gradient1.position = CGPoint(x: size.width / 2, y: size.height / 2)
        gradient1.blendMode = .add
        gradient1.alpha = 0.35
        gradient1.zPosition = -10
        addChild(gradient1)
        gradientLayer1 = gradient1
        
        // Secondary gradient (offset, smaller for depth)
        let gradient2 = createGradientSprite(
            colors: [
                UIColor(red: 0.8, green: 0.3, blue: 0.6, alpha: 0.4),
                UIColor(red: 0.3, green: 0.1, blue: 0.5, alpha: 0.1),
                UIColor.clear
            ],
            size: CGSize(width: size.width * 0.8, height: size.height * 0.6)
        )
        gradient2.position = CGPoint(x: size.width * 0.7, y: size.height * 0.3)
        gradient2.blendMode = .add
        gradient2.alpha = 0.25
        gradient2.zPosition = -9
        addChild(gradient2)
        gradientLayer2 = gradient2
        
        // Add slow drift animation for depth
        let driftUp = SKAction.moveBy(x: 0, y: 30, duration: 20)
        let driftDown = SKAction.moveBy(x: 0, y: -30, duration: 20)
        let driftSequence = SKAction.sequence([driftUp, driftDown])
        gradient1.run(SKAction.repeatForever(driftSequence))
        
        let driftRight = SKAction.moveBy(x: 20, y: 0, duration: 15)
        let driftLeft = SKAction.moveBy(x: -20, y: 0, duration: 15)
        let driftSequence2 = SKAction.sequence([driftRight, driftLeft])
        gradient2.run(SKAction.repeatForever(driftSequence2))
    }
    
    private func createGradientSprite(colors: [UIColor], size: CGSize) -> SKSpriteNode {
        let renderer = UIGraphicsImageRenderer(size: size)
        
        let image = renderer.image { context in
            let center = CGPoint(x: size.width / 2, y: size.height / 2)
            let radius = max(size.width, size.height) / 2
            
            let cgColors = colors.map { $0.cgColor }
            let locations: [CGFloat] = colors.enumerated().map { CGFloat($0.offset) / CGFloat(colors.count - 1) }
            
            if let gradient = CGGradient(
                colorsSpace: CGColorSpaceCreateDeviceRGB(),
                colors: cgColors as CFArray,
                locations: locations
            ) {
                context.cgContext.drawRadialGradient(
                    gradient,
                    startCenter: center,
                    startRadius: 0,
                    endCenter: center,
                    endRadius: radius,
                    options: []
                )
            }
        }
        
        let sprite = SKSpriteNode(texture: SKTexture(image: image))
        sprite.size = size
        return sprite
    }
    
    // MARK: - Background Stars (Static field)
    
    private func setupBackgroundStars() {
        let emitter = SKEmitterNode()
        
        // Dense background star field
        emitter.particleBirthRate = 60
        emitter.particleLifetime = 10
        emitter.particleLifetimeRange = 5
        
        emitter.particleAlpha = 0.5
        emitter.particleAlphaSpeed = 0
        emitter.particleAlphaRange = 0.3
        
        emitter.particleScale = 0.015
        emitter.particleScaleRange = 0.01
        
        emitter.particleColor = SKColor.white
        emitter.particleBlendMode = .add
        
        emitter.position = CGPoint(x: size.width / 2, y: size.height / 2)
        emitter.particlePositionRange = CGVector(dx: size.width * 1.3, dy: size.height * 1.3)
        
        // Minimal movement - these are distant stars
        emitter.particleSpeed = 2
        emitter.particleSpeedRange = 1
        emitter.emissionAngle = .pi / 2
        emitter.emissionAngleRange = .pi * 2
        
        emitter.zPosition = -5
        addChild(emitter)
        backgroundStars = emitter
    }
    
    // MARK: - Twinkling Stars (Foreground, animated)
    
    private func setupTwinklingStars() {
        let emitter = SKEmitterNode()
        
        // Fewer but more prominent twinkling stars
        emitter.particleBirthRate = 15
        emitter.particleLifetime = 6
        emitter.particleLifetimeRange = 3
        
        // Twinkling effect via alpha animation
        emitter.particleAlpha = 0.9
        emitter.particleAlphaSpeed = -0.15
        emitter.particleAlphaRange = 0.4
        
        emitter.particleScale = 0.06
        emitter.particleScaleRange = 0.03
        emitter.particleScaleSpeed = 0.005
        
        emitter.particleColor = SKColor(white: 1.0, alpha: 1.0)
        emitter.particleColorBlendFactor = 0.3
        emitter.particleBlendMode = .add
        
        emitter.position = CGPoint(x: size.width / 2, y: size.height / 2)
        emitter.particlePositionRange = CGVector(dx: size.width * 1.2, dy: size.height * 1.2)
        
        // Gentle upward drift
        emitter.particleSpeed = 10
        emitter.particleSpeedRange = 5
        emitter.emissionAngle = .pi / 2
        emitter.emissionAngleRange = .pi / 3
        
        emitter.zPosition = 0
        addChild(emitter)
        twinklingStars = emitter
    }
    
    // MARK: - Shooting Stars (Occasional)
    
    private func setupShootingStars() {
        scheduleNextShootingStar()
    }
    
    private func scheduleNextShootingStar() {
        shootingStarTimer?.invalidate()
        guard !isPaused else { return }
        
        shootingStarTimer = Timer.scheduledTimer(withTimeInterval: Double.random(in: 8...15), repeats: false) { [weak self] _ in
            guard let self, !self.isPaused else { return }
            self.spawnShootingStar()
            self.scheduleNextShootingStar()
        }
    }
    
    private func spawnShootingStar() {
        let shootingStar = SKShapeNode(ellipseOf: CGSize(width: 3, height: 3))
        shootingStar.fillColor = .white
        shootingStar.strokeColor = .clear
        shootingStar.glowWidth = 2
        
        // Random start position at top/right
        let startX = CGFloat.random(in: size.width * 0.3...size.width)
        let startY = size.height + 20
        shootingStar.position = CGPoint(x: startX, y: startY)
        shootingStar.alpha = 0
        shootingStar.zPosition = 5
        
        addChild(shootingStar)
        
        // Trail effect
        let trail = SKShapeNode()
        let path = CGMutablePath()
        path.move(to: .zero)
        path.addLine(to: CGPoint(x: 40, y: 20))
        trail.path = path
        trail.strokeColor = SKColor(white: 1.0, alpha: 0.6)
        trail.lineWidth = 1.5
        trail.glowWidth = 1
        trail.zRotation = .pi + .pi / 4
        shootingStar.addChild(trail)
        
        // Animation
        let fadeIn = SKAction.fadeIn(withDuration: 0.1)
        let move = SKAction.moveBy(x: -size.width * 0.6, y: -size.height * 0.5, duration: 1.2)
        move.timingMode = .easeIn
        let fadeOut = SKAction.fadeOut(withDuration: 0.3)
        let remove = SKAction.removeFromParent()
        
        shootingStar.run(SKAction.sequence([fadeIn, move, fadeOut, remove]))
    }
}
