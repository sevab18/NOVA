export function LoadingState({ label = 'Загружаем данные…' }: { label?: string }) {
  return <div className="page-state"><span className="loader" />{label}</div>
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="page-state page-state--error">
      <strong>Что-то пошло не так</strong>
      <span>{message}</span>
      {onRetry && <button className="button button--outline" type="button" onClick={onRetry}>Повторить</button>}
    </div>
  )
}
