export default function MediumCard({ article }: { article: any }) {
    return (
      <div className="border p-3 rounded shadow">
        <h4 className="font-semibold">{article.title}</h4>
      </div>
    );
  }
  