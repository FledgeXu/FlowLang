import { createFileRoute } from "@tanstack/react-router";
import "@/App.css";
import { useAnnotatedArticle } from "@/hooks/useAnnotatedArticle";

const ARTICLE_URL =
  "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino";

export const Route = createFileRoute("/")({
  component: RootComponent,
});

function RootComponent() {
  const { html, isLoading, isError, error } = useAnnotatedArticle(ARTICLE_URL);

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  return (
    <div className="mx-auto max-w-3xl p-6">
      <article
        className="prose reader"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}
