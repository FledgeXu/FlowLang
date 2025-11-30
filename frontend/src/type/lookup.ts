export type LookupReq = {
  sentenceId: string;
  wordId: string;
};

export type LookupResp = {
  wordId: string;
  text: string | null;
};
