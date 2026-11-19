import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { BagIcon, UserIcon } from './Icons'


function navClass({ isActive }: { isActive: boolean }) {
  return isActive ? 'nav-link nav-link--active' : 'nav-link'
}

export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="site-shell">
      <div className="announcement">
        <span>Учебный магазин — безопасная оплата появится на следующем этапе</span>
      </div>

      <header className="site-header">
        <div className="container header-inner">
          <NavLink to="/" className="brand" aria-label="NOVA Store — главная">
            <span className="brand-mark">N</span>
            <span>
              <strong>NOVA</strong>
              <small>STORE</small>
            </span>
          </NavLink>

          <nav className="main-nav" aria-label="Основная навигация">
            <NavLink to="/" end className={navClass}>Главная</NavLink>
            <NavLink to="/catalog" className={navClass}>Каталог</NavLink>
            {user?.role === 'admin' && (
              <NavLink to="/admin" className={navClass}>Админ</NavLink>
            )}
          </nav>

          <div className="header-actions">
            {user ? (
              <div className="account-menu">
                <NavLink to="/profile" className="icon-link" aria-label="Профиль">
                  <UserIcon />
                  <span>{user.name.split(' ')[0]}</span>
                </NavLink>
                <button className="text-button" type="button" onClick={logout}>
                  Выйти
                </button>
              </div>
            ) : (
              <NavLink to="/login" className="icon-link">
                <UserIcon />
                <span>Войти</span>
              </NavLink>
            )}
            <NavLink to="/cart" className="bag-link" aria-label="Корзина">
              <BagIcon />
              <span className="bag-count">0</span>
            </NavLink>
          </div>
        </div>
      </header>

      <main className="site-main">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="container footer-grid">
          <div>
            <div className="brand brand--footer">
              <span className="brand-mark">N</span>
              <span><strong>NOVA</strong><small>STORE</small></span>
            </div>
            <p>Учебный full-stack магазин с понятным интерфейсом и безопасным API.</p>
          </div>
          <div>
            <h3>Навигация</h3>
            <NavLink to="/catalog">Каталог</NavLink>
            <NavLink to="/profile">Профиль</NavLink>
          </div>
          <div>
            <h3>Проект</h3>
            <span>React + TypeScript</span>
            <span>FastAPI + PostgreSQL</span>
          </div>
        </div>
        <div className="container footer-bottom">
          <span>© 2026 NOVA Store</span>
          <span>Учебный проект</span>
        </div>
      </footer>
    </div>
  )
}
