import type { ArticleResp, ArticleReq } from "@/type/article";
import { apiClient } from "./client";

export async function fetchArticle(req: ArticleReq): Promise<ArticleResp> {
  const { data } = await apiClient.post<ArticleResp>("/article/fetch", req);
  return data;
}
