import type { ReactNode } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'


export function ProtectedRoute({
  children,
  requireAdmin = false,
}: {
  children: ReactNode
  requireAdmin?: boolean
}) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <div className="page-state"><span className="loader" />Проверяем сессию…</div>
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (requireAdmin && user.role !== 'admin') {
    return (
      <section className="container narrow-page error-page">
        <span className="eyebrow">403 · Доступ ограничен</span>
        <h1>Этот раздел доступен администратору</h1>
        <p>Ваш аккаунт активен, но у него нет прав управления каталогом.</p>
        <Link className="button button--primary" to="/catalog">Вернуться в каталог</Link>
      </section>
    )
  }

  return children
}
