import type {
    LookupReq,
    LookupResp
} from "@/type/lookup";
import { apiClient } from "./client";

export async function lookupWords(req: LookupReq[],
): Promise<LookupResp[]> {
    const { data } = await apiClient.post<LookupResp[]>("/word/lookup", req);
    return data;
}


