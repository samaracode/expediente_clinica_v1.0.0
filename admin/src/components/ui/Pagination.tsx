interface PaginationProps {
  page: number;
  pages: number;
  total: number;
  onPage: (page: number) => void;
}

export default function Pagination({ page, pages, total, onPage }: PaginationProps) {
  if (pages <= 1) return null;

  return (
    <div className="flex items-center justify-between px-1 py-3 text-sm text-gray-500 dark:text-gray-400">
      <span>
        {total} resultado{total !== 1 ? "s" : ""} &middot; Página {page} de {pages}
      </span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPage(page - 1)}
          disabled={page <= 1}
          className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/[0.04]"
        >
          ← Anterior
        </button>
        <button
          onClick={() => onPage(page + 1)}
          disabled={page >= pages}
          className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/[0.04]"
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}
