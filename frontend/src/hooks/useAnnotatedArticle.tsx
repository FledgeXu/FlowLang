import { useMemo, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import parse, {
  attributesToProps,
  domToReact,
  Element,
  type DOMNode,
} from "html-react-parser";
import { fetchArticle } from "@/api/article";
import { lookupWords } from "@/api/lookup";
import type { LookupReq, LookupResp } from "@/type/lookup";
import { cn } from "@/lib/utils";

export function useAnnotatedArticle(url: string) {
  const articleQuery = useQuery<string>({
    queryKey: ["fetch-html", url],
    queryFn: async () => {
      const resp = await fetchArticle({ url });
      return resp.rawHtml;
    },
  });

  const annotatedQuery = useQuery<ReactNode>({
    queryKey: ["annotated-html", url, articleQuery.data],
    enabled: Boolean(articleQuery.data),
    queryFn: () => annotateHtml(articleQuery.data!),
  });

  const fallbackContent = useMemo<ReactNode | null>(() => {
    if (!articleQuery.data) return null;
    return parse(articleQuery.data);
  }, [articleQuery.data]);

  return {
    content: annotatedQuery.data ?? fallbackContent,
    isLoading: articleQuery.isLoading,
    isError: articleQuery.isError,
    error: articleQuery.error,
  };
}

async function annotateHtml(html: string): Promise<ReactNode> {
  const pairs = collectHardWordPairs(html);
  if (pairs.length === 0) return parse(html);

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
    return parse(html);
  }
}

function toLookupMap(results: LookupResp[]) {
  return new Map(results.filter((r) => r.text).map((r) => [r.wordId, r.text!]));
}

function addRubyToHardWords(
  html: string,
  textMap: Map<string, string>,
): ReactNode {
  return parse(html, {
    replace: (domNode) => {
      if (!(domNode instanceof Element)) return;

      const classNames =
        domNode.attribs?.class?.split(/\s+/).filter(Boolean) ?? [];
      const isHardWord = classNames.includes("hard-word");
      if (!isHardWord) return;

      const wordId = domNode.attribs["word-id"];
      if (!wordId) return;

      const rubyText = textMap.get(wordId) ?? "not found"; // fallback placeholder when lookup misses
      const childProps = attributesToProps(domNode.attribs, domNode.name);

      return (
        <Tooltip>
          <TooltipTrigger>
            <span
              {...childProps}
              className={cn(
                childProps.className,
                "underline decoration-dotted underline-offset-4",
              )}
            >
              {domToReact(domNode.children as unknown as DOMNode[])}
            </span>
          </TooltipTrigger>
          <TooltipContent>{rubyText}</TooltipContent>
        </Tooltip>
      );
    },
  });
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
