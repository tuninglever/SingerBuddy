import SwiftUI
import WebKit

struct ContentView: View {
	@StateObject private var viewModel = WebViewViewModel()

	var body: some View {
		WebView(url: viewModel.startURL)
			.ignoresSafeArea(.all)
	}
}

#Preview {
	ContentView()
}
