import type { ArticleResp, ArticleReq } from "@/type/article";
import { apiClient } from "./client";
import type { MindmapReq, MindmapResp } from "@/type/mindTreeNode";

export async function fetchArticle(req: ArticleReq): Promise<ArticleResp> {
  const { data } = await apiClient.post<ArticleResp>("/article/fetch", req);
  return data;
}

export async function fetchMindmap(req: MindmapReq): Promise<MindmapResp> {
  const { data } = await apiClient.post<MindmapResp>("/article/mindmap", req);
  return data;
}
