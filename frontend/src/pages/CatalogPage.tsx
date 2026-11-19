import { useCallback, useEffect, useMemo, useState } from 'react'

import { ApiError, api } from '../api/client'
import { ErrorState, LoadingState } from '../components/PageState'
import { ProductCard } from '../components/ProductCard'
import { SearchIcon } from '../components/Icons'
import type { Category, Product } from '../types'


type SortOption = 'newest' | 'price-asc' | 'price-desc' | 'name'

function fetchCatalogData() {
  return Promise.all([api.products(), api.categories()])
}

export function CatalogPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [categoryId, setCategoryId] = useState('all')
  const [sort, setSort] = useState<SortOption>('newest')

  const loadCatalog = useCallback(() => {
    setLoading(true)
    setError('')
    fetchCatalogData()
      .then(([productList, categoryList]) => {
        setProducts(productList)
        setCategories(categoryList)
      })
      .catch((reason: unknown) => {
        setError(reason instanceof ApiError ? reason.message : 'Backend недоступен')
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let active = true
    fetchCatalogData()
      .then(([productList, categoryList]) => {
        if (!active) return
        setProducts(productList)
        setCategories(categoryList)
      })
      .catch((reason: unknown) => {
        if (!active) return
        setError(reason instanceof ApiError ? reason.message : 'Backend недоступен')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const filteredProducts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    const result = products.filter((product) => {
      const matchesQuery = !normalizedQuery ||
        product.name.toLowerCase().includes(normalizedQuery) ||
        product.description?.toLowerCase().includes(normalizedQuery)
      const matchesCategory = categoryId === 'all' || product.category_id === Number(categoryId)
      return matchesQuery && matchesCategory
    })

    return result.sort((left, right) => {
      if (sort === 'price-asc') return Number(left.price) - Number(right.price)
      if (sort === 'price-desc') return Number(right.price) - Number(left.price)
      if (sort === 'name') return left.name.localeCompare(right.name, 'ru')
      return right.id - left.id
    })
  }, [products, query, categoryId, sort])

  const categoryNames = new Map(categories.map((category) => [category.id, category.name]))

  return (
    <section className="container page-section">
      <div className="catalog-heading">
        <div><span className="eyebrow">Все товары</span><h1>Каталог</h1></div>
        <p>Найдите нужное по названию или категории. Фильтры работают мгновенно.</p>
      </div>

      <div className="catalog-toolbar">
        <label className="search-field">
          <SearchIcon />
          <span className="sr-only">Поиск товаров</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Поиск по каталогу" />
        </label>
        <label>
          <span className="sr-only">Категория</span>
          <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
            <option value="all">Все категории</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
        </label>
        <label>
          <span className="sr-only">Сортировка</span>
          <select value={sort} onChange={(event) => setSort(event.target.value as SortOption)}>
            <option value="newest">Сначала новые</option>
            <option value="price-asc">Цена: по возрастанию</option>
            <option value="price-desc">Цена: по убыванию</option>
            <option value="name">По названию</option>
          </select>
        </label>
      </div>

      <div className="catalog-summary">
        <span>Найдено: <strong>{filteredProducts.length}</strong></span>
        {(query || categoryId !== 'all') && (
          <button type="button" className="text-button" onClick={() => { setQuery(''); setCategoryId('all') }}>
            Сбросить фильтры
          </button>
        )}
      </div>

      {loading && <LoadingState label="Загружаем каталог…" />}
      {!loading && error && <ErrorState message={error} onRetry={loadCatalog} />}
      {!loading && !error && filteredProducts.length === 0 && (
        <div className="empty-panel"><span className="empty-panel__number">0</span><div><h3>Ничего не найдено</h3><p>Измените запрос или сбросьте фильтры.</p></div></div>
      )}
      {!loading && !error && filteredProducts.length > 0 && (
        <div className="product-grid">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              categoryName={product.category_id ? categoryNames.get(product.category_id) : undefined}
            />
          ))}
        </div>
      )}
    </section>
  )
}
