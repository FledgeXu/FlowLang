export type MindTreeNode = {
  text: string;
  children: MindTreeNode[];
};

export type MindmapReq = {
  articleId: string;
};

export type MindmapResp = {
  articleId: string;
  data: MindTreeNode;
};
