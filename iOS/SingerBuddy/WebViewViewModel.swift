import Foundation
import SwiftUI
import WebKit

final class WebViewViewModel: NSObject, ObservableObject, WKNavigationDelegate {
	private let bundleName = "WebResources"
	var schemeHandler: BundleSchemeHandler?

	var startURL: URL? {
		if
			let resourceBundleURL = Bundle.main.url(
				forResource: bundleName,
				withExtension: "bundle"
			),
			let resourceBundle = Bundle(url: resourceBundleURL),
			let indexURL = resourceBundle.url(
				forResource: "index",
				withExtension: "html"
			)
		{
			return indexURL
		}

		// Fallback for non-bundled local runs.
		if let localIndexURL = Bundle.main.url(
			forResource: "index",
			withExtension: "html"
		) {
			return localIndexURL
		}

		assertionFailure("Unable to locate web resources in WebResources.bundle.")
		return nil
	}

	func webView(
		_ webView: WKWebView,
		didFail navigation: WKNavigation!,
		withError error: Error
	) {
		print("Navigation failed: \(error.localizedDescription)")
	}

	func webView(
		_ webView: WKWebView,
		didFailProvisionalNavigation navigation: WKNavigation!,
		withError error: Error
	) {
		print("Provisional navigation failed: \(error.localizedDescription)")
	}
}
