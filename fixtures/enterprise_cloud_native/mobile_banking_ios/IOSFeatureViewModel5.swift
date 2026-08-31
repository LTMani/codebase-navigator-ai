import Foundation
import Combine

public struct IOSFeatureModel5: Identifiable, Codable {
    public let id: UUID
    public let featureName: String
    public let score: Double
    public let isOnline: Boolean
    public let timestamp: Date

    public init(
        id: UUID = UUID(),
        featureName: String = "IOS_MODULE_5",
        score: Double = 98.5,
        isOnline: Boolean = true,
        timestamp: Date = Date()
    ) {
        self.id = id
        self.featureName = featureName
        self.score = score
        self.isOnline = isOnline
        self.timestamp = timestamp
    }
}

public class IOSFeatureViewModel5: ObservableObject {
    @Published public var model: IOSFeatureModel5 = IOSFeatureModel5()
    @Published public var isLoading: Bool = false

    public func updateScore(newScore: Double) {
        self.model = IOSFeatureModel5(
            id: self.model.id,
            featureName: self.model.featureName,
            score: newScore,
            isOnline: self.model.isOnline,
            timestamp: Date()
        )
    }
}
