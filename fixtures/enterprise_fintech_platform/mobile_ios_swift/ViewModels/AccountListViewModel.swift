import Foundation
import Combine

public class AccountListViewModel: ObservableObject {
    @Published public var accounts: [AccountItem] = []
    @Published public var isLoading: Bool = false
    @Published public var errorMessage: String? = nil

    private let service: BankingAPIServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    public init(service: BankingAPIServiceProtocol = BankingAPIService()) {
        self.service = service
        loadAccounts()
    }

    public func loadAccounts() {
        isLoading = true
        errorMessage = nil

        service.fetchAccounts()
            .receive(on: DispatchQueue.main)
            .sink(receiveCompletion: { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                }
            }, receiveValue: { [weak self] items in
                self?.accounts = items
            })
            .store(in: &cancellables)
    }
}
