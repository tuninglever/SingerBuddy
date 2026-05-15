import SwiftUI
import WebKit

final class BundleSchemeHandler: NSObject, WKURLSchemeHandler {
	private let bundleRootURL: URL

	init(bundleRootURL: URL) {
		self.bundleRootURL = bundleRootURL.standardizedFileURL
		super.init()
	}

	func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
		guard let requestURL = urlSchemeTask.request.url else {
			urlSchemeTask.didFailWithError(NSError(domain: "BundleSchemeHandler", code: 1))
			return
		}

		let host = requestURL.host ?? ""
		let pathPart = requestURL.path
		let combinedPath: String
		if host.isEmpty {
			combinedPath = pathPart
		} else if pathPart.isEmpty || pathPart == "/" {
			combinedPath = "/\(host)"
		} else {
			combinedPath = "/\(host)\(pathPart)"
		}

		let rawPath = combinedPath.isEmpty ? "/index.html" : combinedPath
		let trimmed = rawPath.hasPrefix("/") ? String(rawPath.dropFirst()) : rawPath
		let decodedPath = trimmed.removingPercentEncoding ?? trimmed
		let relativePath = decodedPath.isEmpty ? "index.html" : decodedPath

		let fileURL = bundleRootURL.appendingPathComponent(relativePath).standardizedFileURL
		guard fileURL.path.hasPrefix(bundleRootURL.path) else {
			print("[BundleSchemeHandler] Blocked path traversal: \(requestURL.absoluteString)")
			urlSchemeTask.didFailWithError(NSError(domain: "BundleSchemeHandler", code: 2))
			return
		}

		do {
			let data = try Data(contentsOf: fileURL)
			let mime = mimeType(for: fileURL.pathExtension)
			let response = HTTPURLResponse(
				url: requestURL,
				statusCode: 200,
				httpVersion: "HTTP/1.1",
				headerFields: [
					"Content-Type": mime,
					"Content-Length": "\(data.count)"
				]
			) ?? URLResponse(
				url: requestURL,
				mimeType: mime,
				expectedContentLength: data.count,
				textEncodingName: "utf-8"
			)
			urlSchemeTask.didReceive(response)
			urlSchemeTask.didReceive(data)
			urlSchemeTask.didFinish()
		} catch {
			print("[BundleSchemeHandler] Missing resource for \(requestURL.absoluteString) -> \(fileURL.path)")
			urlSchemeTask.didFailWithError(error)
		}
	}

	func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

	private func mimeType(for ext: String) -> String {
		switch ext.lowercased() {
		case "html": return "text/html"
		case "css": return "text/css"
		case "js": return "application/javascript"
		case "json": return "application/json"
		case "svg": return "image/svg+xml"
		case "png": return "image/png"
		case "jpg", "jpeg": return "image/jpeg"
		case "ico": return "image/x-icon"
		case "mei", "xml": return "application/xml"
		case "pat": return "application/octet-stream"
		default: return "application/octet-stream"
		}
	}
}

struct WebView: UIViewRepresentable {
	let url: URL?

	func makeUIView(context: Context) -> WKWebView {
		let bundleRootURL = url?.deletingLastPathComponent() ?? Bundle.main.bundleURL
		let handler = BundleSchemeHandler(bundleRootURL: bundleRootURL)
		context.coordinator.schemeHandler = handler

		let configuration = WKWebViewConfiguration()
		configuration.setURLSchemeHandler(handler, forURLScheme: "app")
		configuration.allowsInlineMediaPlayback = true
		configuration.mediaTypesRequiringUserActionForPlayback = []

		let webView = WKWebView(frame: .zero, configuration: configuration)
		webView.navigationDelegate = context.coordinator
		webView.isInspectable = true
		webView.scrollView.bounces = false

		if let appURL = URL(string: "app:///index.html") {
			webView.load(URLRequest(url: appURL))
		}

		return webView
	}

	func updateUIView(_ uiView: WKWebView, context: Context) {}

	func makeCoordinator() -> WebViewViewModel {
		WebViewViewModel()
	}
}
