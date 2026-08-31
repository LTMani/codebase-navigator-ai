import Foundation
import Combine

public protocol BankingAPIServiceProtocol {
    func fetchAccounts() -> AnyPublisher<[AccountItem], Error>
    func transferFunds(sourceId: UUID, targetId: UUID, amount: Double) -> AnyPublisher<Bool, Error>
}

public class BankingAPIService: BankingAPIServiceProtocol {
    private let baseURL: URL

    public init(baseURL: URL = URL(string: "https://api.navigator-fintech.internal/v1")!) {
        self.baseURL = baseURL
    }

    public func fetchAccounts() -> AnyPublisher<[AccountItem], Error> {
        let mockAccounts: [AccountItem] = [
            AccountItem(accountNumber: "US-8849-0012", holderName: "Enterprise Primary Ops", balance: 489201.50, category: .checking),
            AccountItem(accountNumber: "US-8849-0099", holderName: "Payroll Escrow Reserve", balance: 1250000.00, category: .savings),
            AccountItem(accountNumber: "US-8849-0341", holderName: "Corporate Venture Reserve", balance: 850400.25, category: .wealth)
        ]

        return Just(mockAccounts)
            .setFailureType(to: Error.self)
            .delay(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    public func transferFunds(sourceId: UUID, targetId: UUID, amount: Double) -> AnyPublisher<Bool, Error> {
        guard amount > 0 else {
            return Fail(error: NSError(domain: "BankingService", code: 400, userInfo: [NSLocalizedDescriptionKey: "Invalid transfer amount"]))
                .eraseToAnyPublisher()
        }

        return Just(true)
            .setFailureType(to: Error.self)
            .delay(for: .milliseconds(400), scheduler: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}
