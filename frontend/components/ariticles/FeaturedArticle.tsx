export default function FeaturedArticle({ article }: { article: any }) {
    return (
      <div className="border p-4 rounded-lg shadow">
        <h3 className="font-bold text-xl">{article.title}</h3>
        <p>{article.description}</p>
      </div>
    );
  }
  