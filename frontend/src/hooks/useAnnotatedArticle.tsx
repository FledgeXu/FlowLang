import { useQuery } from "@tanstack/react-query";
import parse from "html-react-parser";
import { type ReactNode, useMemo } from "react";
import { fetchArticle } from "@/api/article";
import { annotateHtml } from "@/services/article";

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
