export const DEVELOPER_CREDIT = {
  text: "Разработано TDDaniel",
  url: "https://tddaniel.netlify.app",
};

export default function DeveloperCredit({ className = "" }: { className?: string }) {
  return (
    <div className={`developer-credit ${className}`} data-testid="developer-credit">
      <a
        href={DEVELOPER_CREDIT.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-xs text-[var(--text-muted,#717680)] hover:text-[var(--primary,#0c7c59)] transition-colors py-1 px-2 rounded font-medium"
      >
        <span>{DEVELOPER_CREDIT.text}</span>
        <svg
          className="w-3 h-3 opacity-70"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
          />
        </svg>
      </a>
    </div>
  );
}
