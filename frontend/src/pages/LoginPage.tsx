import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/useAuth'


export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/profile" replace />

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await login({ email, password })
      const destination = (location.state as { from?: string } | null)?.from ?? '/profile'
      navigate(destination, { replace: true })
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : 'Не удалось войти')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-page container">
      <div className="auth-aside">
        <span className="eyebrow eyebrow--light">С возвращением</span>
        <h1>Ваш каталог всегда рядом.</h1>
        <p>Войдите, чтобы открыть профиль и продолжить работу с магазином.</p>
        <div className="auth-aside__number">01</div>
      </div>
      <div className="auth-card">
        <div className="auth-card__heading"><span>Вход</span><h2>Добро пожаловать</h2></div>
        <form onSubmit={handleSubmit} className="form-stack">
          <label className="field">
            <span>Email</span>
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required placeholder="you@example.com" />
          </label>
          <label className="field">
            <span>Пароль</span>
            <input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required placeholder="Ваш пароль" />
          </label>
          {error && <div className="form-error" role="alert">{error}</div>}
          <button className="button button--primary button--wide" type="submit" disabled={submitting}>
            {submitting ? 'Входим…' : 'Войти'}
          </button>
        </form>
        <p className="auth-switch">Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
      </div>
    </section>
  )
}
