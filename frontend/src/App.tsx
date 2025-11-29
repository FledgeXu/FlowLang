import "@/App.css";
import { apiClient } from "@/api/client";
import { useQuery } from "@tanstack/react-query";

function App() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["html"],
    queryFn: async () => {
      const resp = await apiClient.post<string>("/article/fetch", {
        url: "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino",
      });
      return resp.data.text;
    },
  });

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  return (
    <div className="mx-auto max-w-3xl p-6">
      <article
        className="prose"
        dangerouslySetInnerHTML={{ __html: data ?? "" }}
      />
    </div>
  );
}

export default App;
