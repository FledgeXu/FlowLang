export type ArticleReq = {
  url: string;
};

export type ArticleResp = {
  title: string,
  author: string,
  lang: string
  rawHtml: string;
};
