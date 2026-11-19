import { Link } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { formatDate } from '../utils/format'


export function ProfilePage() {
  const { user, logout } = useAuth()
  if (!user) return null

  return (
    <section className="container page-section profile-page">
      <div className="section-heading">
        <div><span className="eyebrow">Личный кабинет</span><h1>Здравствуйте, {user.name}</h1></div>
        <button className="button button--outline" type="button" onClick={logout}>Выйти</button>
      </div>

      <div className="profile-grid">
        <article className="profile-card profile-card--main">
          <div className="avatar">{user.name.slice(0, 1).toUpperCase()}</div>
          <div><span>Имя</span><strong>{user.name}</strong></div>
          <div><span>Email</span><strong>{user.email}</strong></div>
          <div><span>Роль</span><strong>{user.role === 'admin' ? 'Администратор' : 'Покупатель'}</strong></div>
          <div><span>С нами с</span><strong>{formatDate(user.created_at)}</strong></div>
        </article>

        <article className="profile-card profile-card--accent">
          <span className="eyebrow eyebrow--light">Следующий этап</span>
          <h2>История заказов появится здесь</h2>
          <p>После реализации корзины и оформления покупок профиль станет центром управления заказами.</p>
          <Link className="button button--light" to="/catalog">Перейти в каталог</Link>
        </article>
      </div>
    </section>
  )
}
