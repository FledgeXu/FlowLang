import { useQuery } from "@tanstack/react-query";
import { fetchArticle } from "@/api/article";
import { lookupWords } from "@/api/lookup";
import type { LookupReq, LookupResp } from "@/type/lookup";

export function useAnnotatedArticle(url: string) {
  const articleQuery = useQuery({
    queryKey: ["fetch-html", url],
    queryFn: async () => {
      const resp = await fetchArticle({ url });
      return resp.rawHtml;
    },
  });

  const annotatedQuery = useQuery({
    queryKey: ["annotated-html", url, articleQuery.data],
    enabled: Boolean(articleQuery.data),
    queryFn: () => annotateHtml(articleQuery.data!),
  });

  return {
    html: annotatedQuery.data ?? articleQuery.data ?? "",
    isLoading: articleQuery.isLoading,
    isError: articleQuery.isError,
    error: articleQuery.error,
  };
}

async function annotateHtml(html: string): Promise<string> {
  const pairs = collectHardWordPairs(html);
  if (pairs.length === 0) return html;

  try {
    const req: LookupReq[] = pairs.map(({ sentenceId, wordId }) => ({
      sentenceId,
      wordId,
    }));

    const lookupResp = await lookupWords(req);
    const textMap = toLookupMap(lookupResp);

    return addRubyToHardWords(html, textMap);
  } catch (e) {
    console.error("lookupWords failed", e);
    return html;
  }
}

function toLookupMap(results: LookupResp[]) {
  return new Map(
    results.flatMap(({ wordId, text }) => (text ? [[wordId, text]] : [])),
  );
}

function addRubyToHardWords(
  html: string,
  textMap: Map<string, string>,
): string {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const hardWordNodes = Array.from(
    doc.querySelectorAll<HTMLElement>(".hard-word"),
  );

  hardWordNodes
    .map((node) => ({
      node,
      wordId: node.getAttribute("word-id"),
      sentenceNode: node.closest<HTMLElement>("span.sent[sent-id]"),
      displayText: node.textContent?.trim() || "",
    }))
    .filter(
      ({ wordId, sentenceNode, displayText }) =>
        Boolean(wordId) && Boolean(sentenceNode) && Boolean(displayText),
    )
    .forEach(({ node, wordId }) => {
      const rubyText = textMap.get(wordId!) ?? "not found"; // fallback placeholder when lookup misses

      const ruby = doc.createElement("ruby");
      const rt = doc.createElement("rt");

      rt.textContent = rubyText;

      node.replaceWith(ruby);
      ruby.appendChild(node);
      ruby.appendChild(rt);
    });

  // Return only the body inner HTML
  return doc.body.innerHTML;
}

export type HardWordPair = {
  sentenceId: string;
  wordId: string;
};

// Collect unique [sentId, wordId] pairs from the HTML
export function collectHardWordPairs(html: string): HardWordPair[] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const seenKeys = new Set<string>();

  return Array.from(doc.querySelectorAll<HTMLElement>(".hard-word")).reduce<
    HardWordPair[]
  >((pairs, node) => {
    const wordId = node.getAttribute("word-id");
    const sentenceNode = node.closest<HTMLElement>("span.sent[sent-id]");
    const sentenceId = sentenceNode?.getAttribute("sent-id");

    if (!wordId || !sentenceId) return pairs;

    const key = `${sentenceId}:${wordId}`;
    if (seenKeys.has(key)) return pairs;
    seenKeys.add(key);

    return [...pairs, { sentenceId, wordId }];
  }, []);
}
