import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ApiError, api } from '../api/client'
import { ErrorState, LoadingState } from '../components/PageState'
import { ProductVisual } from '../components/ProductVisual'
import type { Category, Product } from '../types'
import { formatPrice } from '../utils/format'


export function ProductPage() {
  const { productId } = useParams()
  const parsedProductId = Number(productId)
  const invalidProductId = !Number.isInteger(parsedProductId) || parsedProductId <= 0
  const [product, setProduct] = useState<Product | null>(null)
  const [category, setCategory] = useState<Category | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (invalidProductId) return

    Promise.all([api.product(parsedProductId), api.categories()])
      .then(([item, categoryList]) => {
        setProduct(item)
        setCategory(categoryList.find((entry) => entry.id === item.category_id) ?? null)
      })
      .catch((reason: unknown) => {
        setError(reason instanceof ApiError && reason.status === 404 ? 'Товар не найден' : 'Не удалось загрузить товар')
      })
      .finally(() => setLoading(false))
  }, [invalidProductId, parsedProductId])

  if (invalidProductId) return <div className="container page-section"><ErrorState message="Некорректный номер товара" /></div>
  if (loading) return <LoadingState label="Открываем товар…" />
  if (error || !product) return <div className="container page-section"><ErrorState message={error || 'Товар не найден'} /></div>

  return (
    <section className="container page-section">
      <nav className="breadcrumbs" aria-label="Хлебные крошки">
        <Link to="/catalog">Каталог</Link><span>/</span><span>{product.name}</span>
      </nav>
      <div className="product-detail">
        <ProductVisual productId={product.id} name={product.name} large />
        <div className="product-detail__info">
          <span className="eyebrow">{category?.name ?? 'NOVA SELECT'}</span>
          <h1>{product.name}</h1>
          <p className="product-detail__description">
            {product.description ?? 'Описание товара появится после обновления каталога.'}
          </p>
          <strong className="product-detail__price">{formatPrice(product.price)}</strong>
          <div className="availability-row">
            <span className={product.stock > 0 ? 'status-dot status-dot--success' : 'status-dot status-dot--error'} />
            {product.stock > 0 ? `В наличии — ${product.stock} шт.` : 'Нет в наличии'}
          </div>
          <button className="button button--primary button--wide" type="button" disabled>
            Корзина появится на следующем этапе
          </button>
          <div className="detail-notes">
            <div><strong>Безопасно</strong><span>Цена и остаток проверяются backend</span></div>
            <div><strong>Прозрачно</strong><span>Никаких скрытых списаний</span></div>
          </div>
        </div>
      </div>
    </section>
  )
}
