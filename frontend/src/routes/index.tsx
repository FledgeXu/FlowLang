import { createFileRoute } from "@tanstack/react-router";
// import "@/App.css";
import { useAnnotatedArticle } from "@/hooks/useAnnotatedArticle";
import { Card, CardContent } from "@/components/ui/card";

const ARTICLE_URL =
  "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino";

export const Route = createFileRoute("/")({
  component: RootComponent,
});

function RootComponent() {
  const { content, isLoading, isError, error } =
    useAnnotatedArticle(ARTICLE_URL);

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  return (
    <div className="m-4 p-4">
      <Card>
        <CardContent>
          <div className="prose max-w-none">{content}</div>
        </CardContent>
      </Card>
    </div>
  );
}
