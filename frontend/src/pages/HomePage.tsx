import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import { ArrowIcon } from '../components/Icons'
import { ProductCard } from '../components/ProductCard'
import type { Category, Product } from '../types'


export function HomePage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])

  useEffect(() => {
    Promise.all([api.products(), api.categories()])
      .then(([productPage, categoryList]) => {
        setProducts(productPage.items.slice(0, 4))
        setCategories(categoryList)
      })
      .catch(() => undefined)
  }, [])

  const categoryNames = new Map(categories.map((category) => [category.id, category.name]))

  return (
    <>
      <section className="hero-section">
        <div className="container hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">Новая глава вашего стиля</span>
            <h1>Вещи, которые делают обычный день особенным.</h1>
            <p>
              Спокойный дизайн, честные цены и понятный выбор. NOVA собирает
              универсальный каталог без визуального шума.
            </p>
            <div className="hero-actions">
              <Link to="/catalog" className="button button--primary">
                Смотреть каталог <ArrowIcon />
              </Link>
              <Link to="/register" className="button button--ghost">Создать аккаунт</Link>
            </div>
          </div>

          <div className="hero-art" aria-label="Коллекция NOVA">
            <div className="hero-art__card hero-art__card--back">
              <span>ESSENTIAL</span>
              <strong>02</strong>
            </div>
            <div className="hero-art__card hero-art__card--front">
              <span className="hero-art__edition">NOVA / 2026</span>
              <div className="hero-art__object"><span>N</span></div>
              <div>
                <small>SELECTED GOODS</small>
                <strong>Коллекция<br />на каждый день</strong>
              </div>
            </div>
            <span className="hero-stamp">NEW<br />DROP</span>
          </div>
        </div>
      </section>

      <section className="benefits-bar">
        <div className="container benefits-grid">
          <div><strong>01</strong><span>Прозрачный остаток</span></div>
          <div><strong>02</strong><span>Безопасный аккаунт</span></div>
          <div><strong>03</strong><span>Удобно на любом экране</span></div>
        </div>
      </section>

      <section className="section container">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Каталог</span>
            <h2>Выбор редакции</h2>
          </div>
          <Link className="inline-link" to="/catalog">Все товары <ArrowIcon /></Link>
        </div>

        {products.length > 0 ? (
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                categoryName={product.category_id ? categoryNames.get(product.category_id) : undefined}
              />
            ))}
          </div>
        ) : (
          <div className="empty-panel">
            <span className="empty-panel__number">01</span>
            <div><h3>Каталог готов к наполнению</h3><p>Добавьте товары через административный раздел.</p></div>
          </div>
        )}
      </section>

      <section className="container editorial-banner">
        <div>
          <span className="eyebrow eyebrow--light">NOVA MEMBERS</span>
          <h2>Один аккаунт — вся история покупок в одном месте.</h2>
        </div>
        <Link to="/register" className="button button--light">Присоединиться</Link>
      </section>
    </>
  )
}
