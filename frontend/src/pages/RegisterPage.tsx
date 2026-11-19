import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/useAuth'


export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
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
      await register({ name, email, password })
      navigate('/profile', { replace: true })
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : 'Не удалось зарегистрироваться')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-page container">
      <div className="auth-aside auth-aside--burgundy">
        <span className="eyebrow eyebrow--light">NOVA MEMBERS</span>
        <h1>Начните с простого аккаунта.</h1>
        <p>История покупок, профиль и корзина будут собраны в одном месте.</p>
        <div className="auth-aside__number">02</div>
      </div>
      <div className="auth-card">
        <div className="auth-card__heading"><span>Регистрация</span><h2>Создать аккаунт</h2></div>
        <form onSubmit={handleSubmit} className="form-stack">
          <label className="field">
            <span>Имя</span>
            <input autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} minLength={1} maxLength={100} required placeholder="Ваше имя" />
          </label>
          <label className="field">
            <span>Email</span>
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required placeholder="you@example.com" />
          </label>
          <label className="field">
            <span>Пароль</span>
            <input type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} maxLength={128} required placeholder="Минимум 8 символов" />
            <small>От 8 до 128 символов</small>
          </label>
          {error && <div className="form-error" role="alert">{error}</div>}
          <button className="button button--primary button--wide" type="submit" disabled={submitting}>
            {submitting ? 'Создаём аккаунт…' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth-switch">Уже есть аккаунт? <Link to="/login">Войти</Link></p>
      </div>
    </section>
  )
}
