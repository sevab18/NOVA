import { Link } from 'react-router-dom'


export function NotFoundPage() {
  return (
    <section className="container narrow-page error-page">
      <span className="error-code">404</span>
      <h1>Такой страницы нет</h1>
      <p>Возможно, адрес изменился или ссылка была введена с ошибкой.</p>
      <Link className="button button--primary" to="/">На главную</Link>
    </section>
  )
}
