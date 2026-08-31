// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FintechMobileIOS",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "FintechMobileIOS",
            targets: ["FintechMobileIOS"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.1"),
    ],
    targets: [
        .target(
            name: "FintechMobileIOS",
            dependencies: ["Alamofire"]
        ),
        .testTarget(
            name: "FintechMobileIOSTests",
            dependencies: ["FintechMobileIOS"]
        ),
    ]
)
