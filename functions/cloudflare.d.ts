// Ambient types for the Cloudflare Pages Functions runtime used in functions/.
// The full set lives in @cloudflare/workers-types; we declare only what this
// project references so `tsc --noEmit` passes without pulling the whole package.

declare class HTMLRewriter {
  constructor();
  on(selector: string, handlers: ElementHandlers): HTMLRewriter;
  transform(response: Response): Response;
}

interface Element {
  setAttribute(name: string, value: string): Element;
  getAttribute(name: string): string | null;
  setInnerContent(content: string, options?: { html?: boolean }): Element;
  remove(): void;
}

interface ElementHandlers {
  element?(element: Element): void | Promise<void>;
}
