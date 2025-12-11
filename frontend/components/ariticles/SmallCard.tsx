export default function SmallCard({ article }: { article: any }) {
    return (
      <div className="border p-2 rounded shadow-sm">
        <h5>{article.title}</h5>
      </div>
    );
  }
  