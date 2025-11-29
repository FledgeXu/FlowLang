import "@/App.css";
import { apiClient } from "@/api/client";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

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

  const [enhancedHtml, setEnhancedHtml] = useState<string | null>(null);

  useEffect(() => {
    if (!data) return;

    setEnhancedHtml(null);

    requestAnimationFrame(() => {
      const htmlWithRuby = addRubyToHardWords(data);
      setEnhancedHtml(htmlWithRuby);
    });
  }, [data]);

  if (isLoading) return <>Loading...</>;
  if (isError) return <>Error: {(error as Error).message}</>;

  const htmlToRender = enhancedHtml ?? data ?? "";

  return (
    <div className="mx-auto max-w-3xl p-6">
      <article
        className="prose"
        dangerouslySetInnerHTML={{ __html: htmlToRender }}
      />
    </div>
  );
}

export default App;

function addRubyToHardWords(html: string): string {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const hardWords = doc.querySelectorAll<HTMLElement>(".hard-word");

  hardWords.forEach((node) => {
    const text = node.textContent?.trim() || "";
    if (!text) return;

    const ruby = doc.createElement("ruby");
    const rt = doc.createElement("rt");

    rt.textContent = getRubyText(text);

    // <ruby><span class="word hard-word">word</span><rt>ruby word</rt></ruby>
    node.replaceWith(ruby);
    ruby.appendChild(node);
    ruby.appendChild(rt);
  });

  return doc.body.innerHTML;
}

function getRubyText(word: string): string {
  console.log(word);
  return "placeholder";
}
