// MarkdownTextView.swift
// Lightweight Markdown renderer for AI explanations

import SwiftUI

struct MarkdownTextView: View {
    let markdown: String
    var font: Font = .body
    var lineSpacing: CGFloat = 5
    var textAlignment: TextAlignment = .leading

    private var attributed: AttributedString? {
        // Avoid crashing on malformed markdown.
        // AttributedString(markdown:) supports a useful subset and is enough for headings/bullets.
        return try? AttributedString(markdown: markdown)
    }

    var body: some View {
        Group {
            if let attributed {
                Text(attributed)
            } else {
                Text(markdown)
            }
        }
        .font(font)
        .lineSpacing(lineSpacing)
        .multilineTextAlignment(textAlignment)
        .textSelection(.enabled)
        .frame(maxWidth: .infinity, alignment: .leading)
        .tint(.purple)
    }
}

#Preview {
    ScrollView {
        MarkdownTextView(
            markdown: """
            ## TL;DR\n\nToday is a good day to move slowly and choose one priority.\n\n### Key takeaways\n- Focus on one thing\n- Be kind to yourself\n\n### Practical tip\nTry a 10-minute walk.
            """,
            font: .callout
        )
        .padding()
    }
    .background(Color.black)
    .preferredColorScheme(.dark)
}
