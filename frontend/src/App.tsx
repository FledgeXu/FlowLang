import { apiClient } from "@/api/client";
import { useQuery } from "@tanstack/react-query";

function App() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["html"],
    queryFn: async () => {
      const resp = await apiClient.get<string>("/", { responseType: "text" });
      return resp.data;
    },
  });

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  return <div dangerouslySetInnerHTML={{ __html: data ?? "" }} />;
}

export default App;
