type PageHeaderProps = {
  title: string;
  subtitle: string;
  eyebrow?: string;
};

export function PageHeader({ title, subtitle, eyebrow = "Production monitoring" }: PageHeaderProps) {
  return (
    <header className="page-header">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </header>
  );
}
