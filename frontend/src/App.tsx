import { apiClient } from "@/api/client";
import { useQuery } from "@tanstack/react-query";

function App() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["html"],
    queryFn: async () => {
      const resp = await apiClient.post<string>("/article/fetch", {
        url: "https://worksinprogress.co/issue/the-great-downzoning/",
      });
      return resp.data.text;
    },
  });

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  return <div dangerouslySetInnerHTML={{ __html: data ?? "" }} />;
}

export default App;
