import "@/App.css";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { fetchArticle } from "@/api/article";
import { lookupWords } from "@/api/lookup";
import type { LookupReq, LookupResp } from "@/type/lookup";

function App() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["fetch-html"],
    queryFn: async () => {
      const resp = await fetchArticle({
        url: "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino",
      });
      return resp.text; // 后端 ArticleResp.text 是 HTML
    },
  });

  const [enhancedHtml, setEnhancedHtml] = useState<string | null>(null);

  useEffect(() => {
    if (!data) return;

    let cancelled = false;
    setEnhancedHtml(null);

    (async () => {
      const pairs = collectHardWordPairs(data);
      if (pairs.length === 0) {
        if (!cancelled) setEnhancedHtml(data);
        return;
      }

      const req: LookupReq[] = pairs.map(([sentenceId, wordId]) => ({
        sentenceId,
        wordId,
      }));

      let lookupResp: LookupResp[];
      try {
        lookupResp = await lookupWords(req);
      } catch (e) {
        console.error("lookupWords failed", e);
        if (!cancelled) setEnhancedHtml(data);
        return;
      }

      const textMap = new Map<string, string>();
      lookupResp.forEach(({ wordId, text }) => {
        if (!text) return;
        textMap.set(wordId, text);
      });
      console.log(lookupResp);

      const htmlWithRuby = addRubyToHardWords(data, textMap);

      if (!cancelled) {
        setEnhancedHtml(htmlWithRuby);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [data]);

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  const htmlToRender = enhancedHtml ?? data ?? "";

  return (
    <div className="mx-auto max-w-3xl p-6">
      <article
        className="prose reader"
        dangerouslySetInnerHTML={{ __html: htmlToRender }}
      />
    </div>
  );
}

export default App;

function addRubyToHardWords(
  html: string,
  textMap: Map<string, string>,
): string {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const hardWords = doc.querySelectorAll<HTMLElement>(".hard-word");

  hardWords.forEach((node) => {
    const displayText = node.textContent?.trim() || "";
    if (!displayText) return;

    const wordId = node.getAttribute("word-id");
    if (!wordId) return;

    const sentSpan = node.closest<HTMLElement>("span.sent[sent-id]");
    if (!sentSpan) return;

    const sentId = sentSpan.getAttribute("sent-id");
    if (!sentId) return;


    console.log(textMap.get(wordId))

    const rubyText = textMap.get(wordId) ?? "not found"; // 查不到就用原词

    const ruby = doc.createElement("ruby");
    const rt = doc.createElement("rt");

    rt.textContent = rubyText;

    // <ruby><span class="word hard-word">word</span><rt>解释</rt></ruby>
    node.replaceWith(ruby);
    ruby.appendChild(node);
    ruby.appendChild(rt);
  });

  // 只拿 body 里的内容
  return doc.body.innerHTML;
}

/**
 * 从 HTML 中收集所有 .hard-word，并返回 [sentId, wordId][]
 */
export function collectHardWordPairs(html: string): string[][] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const hardWords = doc.querySelectorAll<HTMLElement>(".hard-word");

  const result: string[][] = [];
  const seen = new Set<string>();

  hardWords.forEach((node) => {
    const wordId = node.getAttribute("word-id");
    if (!wordId) return;

    const sentSpan = node.closest<HTMLElement>("span.sent[sent-id]");
    if (!sentSpan) return;

    const sentId = sentSpan.getAttribute("sent-id");
    if (!sentId) return;

    const key = `${sentId}:${wordId}`;
    if (seen.has(key)) return;
    seen.add(key);

    result.push([sentId, wordId]);
  });

  return result;
}
