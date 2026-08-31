import Foundation

public enum AccountCategory: String, Codable, CaseIterable {
    case checking = "CHECKING"
    case savings = "SAVINGS"
    case credit = "CREDIT"
    case wealth = "WEALTH"
}

public struct AccountItem: Identifiable, Codable {
    public let id: UUID
    public let accountNumber: String
    public let holderName: String
    public let balance: Double
    public let currency: String
    public let category: AccountCategory
    public let isLocked: Bool
    public let updatedAt: Date

    public init(
        id: UUID = UUID(),
        accountNumber: String,
        holderName: String,
        balance: Double,
        currency: String = "USD",
        category: AccountCategory,
        isLocked: Bool = false,
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.accountNumber = accountNumber
        self.holderName = holderName
        self.balance = balance
        self.currency = currency
        self.category = category
        self.isLocked = isLocked
        self.updatedAt = updatedAt
    }
}
