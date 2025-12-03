import parse, {
  attributesToProps,
  type DOMNode,
  domToReact,
  Element,
} from "html-react-parser";
import { type ReactNode } from "react";
import { lookupWords } from "@/api/lookup";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { LookupReq, LookupResp } from "@/type/lookup";

type HardWordPair = {
  sentenceId: string;
  wordId: string;
};

type ReplaceRule = (
  domNode: DOMNode,
  index: number,
) => Element | string | null | boolean | object | void;

export async function annotateHtml(html: string): Promise<ReactNode> {
  const pairs = extractHardWordPairs(html);
  if (pairs.length === 0) return parse(html);

  try {
    const req: LookupReq[] = pairs.map(({ sentenceId, wordId }) => ({
      sentenceId,
      wordId,
    }));

    const lookupResp = await lookupWords(req);
    const textMap = toLookupMap(lookupResp);

    return decorateHtml(html, textMap);
  } catch (e) {
    console.error("lookupWords failed", e);
    return parse(html);
  }
}

function toLookupMap(results: LookupResp[]) {
  return new Map(results.filter((r) => r.text).map((r) => [r.wordId, r.text!]));
}

// Collect unique [sentId, wordId] pairs from the HTML
function extractHardWordPairs(html: string): HardWordPair[] {
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

function makeHardWordRule(textMap: Map<string, string>): ReplaceRule {
  return (domNode, _index) => {
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
          <span {...childProps}>
            {domToReact(domNode.children as unknown as DOMNode[])}
          </span>
        </TooltipTrigger>
        <TooltipContent>{rubyText}</TooltipContent>
      </Tooltip>
    );
  };
}

function decorateHtml(html: string, textMap: Map<string, string>): ReactNode {
  const rules: ReplaceRule[] = [makeHardWordRule(textMap)];
  return parse(html, {
    replace: (domNode, index) => {
      for (const rule of rules) {
        const result = rule(domNode, index);
        if (result !== undefined) {
          return result;
        }
      }
      return;
    },
  });
}
