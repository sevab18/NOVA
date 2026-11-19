import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { ApiError, api } from '../api/client'
import { ErrorState, LoadingState } from '../components/PageState'
import type { Category, Product } from '../types'
import { formatPrice } from '../utils/format'


type AdminTab = 'products' | 'categories'

function fetchAdminData() {
  return Promise.all([api.products(), api.categories()])
}

export function AdminPage() {
  const [tab, setTab] = useState<AdminTab>('products')
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const [productName, setProductName] = useState('')
  const [productDescription, setProductDescription] = useState('')
  const [productPrice, setProductPrice] = useState('')
  const [productStock, setProductStock] = useState('0')
  const [productCategory, setProductCategory] = useState('')

  const [categoryName, setCategoryName] = useState('')
  const [categoryDescription, setCategoryDescription] = useState('')
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const loadData = useCallback(() => {
    setLoading(true)
    setError('')
    fetchAdminData()
      .then(([productPage, categoryList]) => {
        setProducts(productPage.items)
        setCategories(categoryList)
      })
      .catch((reason: unknown) => {
        setError(reason instanceof ApiError ? reason.message : 'Не удалось загрузить данные')
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let active = true
    fetchAdminData()
      .then(([productPage, categoryList]) => {
        if (!active) return
        setProducts(productPage.items)
        setCategories(categoryList)
      })
      .catch((reason: unknown) => {
        if (!active) return
        setError(reason instanceof ApiError ? reason.message : 'Не удалось загрузить данные')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const showError = (reason: unknown, fallback: string) => {
    setError(reason instanceof ApiError ? reason.message : fallback)
    setNotice('')
  }

  const handleProductSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      const product = await api.createProduct({
        name: productName,
        description: productDescription.trim() || null,
        price: productPrice,
        stock: Number(productStock),
        category_id: productCategory ? Number(productCategory) : null,
      })
      setProducts((current) => [...current, product])
      setProductName('')
      setProductDescription('')
      setProductPrice('')
      setProductStock('0')
      setProductCategory('')
      setNotice(`Товар «${product.name}» создан`)
    } catch (reason) {
      showError(reason, 'Не удалось создать товар')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCategorySubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      if (editingCategory) {
        const updated = await api.updateCategory(editingCategory.id, {
          name: categoryName,
          description: categoryDescription.trim() || null,
        })
        setCategories((current) => current.map((item) => item.id === updated.id ? updated : item))
        setNotice(`Категория «${updated.name}» обновлена`)
      } else {
        const created = await api.createCategory({
          name: categoryName,
          description: categoryDescription.trim() || null,
        })
        setCategories((current) => [...current, created])
        setNotice(`Категория «${created.name}» создана`)
      }
      cancelCategoryEdit()
    } catch (reason) {
      showError(reason, 'Не удалось сохранить категорию')
    } finally {
      setSubmitting(false)
    }
  }

  const startCategoryEdit = (category: Category) => {
    setEditingCategory(category)
    setCategoryName(category.name)
    setCategoryDescription(category.description ?? '')
    setError('')
    setNotice('')
  }

  const cancelCategoryEdit = () => {
    setEditingCategory(null)
    setCategoryName('')
    setCategoryDescription('')
  }

  const deleteCategory = async (category: Category) => {
    if (!window.confirm(`Удалить категорию «${category.name}»?`)) return
    setError('')
    setNotice('')
    try {
      await api.deleteCategory(category.id)
      setCategories((current) => current.filter((item) => item.id !== category.id))
      setNotice(`Категория «${category.name}» удалена`)
    } catch (reason) {
      showError(reason, 'Не удалось удалить категорию')
    }
  }

  const categoryNames = new Map(categories.map((category) => [category.id, category.name]))

  return (
    <section className="container page-section admin-page">
      <div className="catalog-heading">
        <div><span className="eyebrow">Управление магазином</span><h1>Админ-панель</h1></div>
        <p>Изменения отправляются в FastAPI и сразу сохраняются в PostgreSQL.</p>
      </div>

      <div className="admin-tabs" role="tablist" aria-label="Разделы админ-панели">
        <button type="button" className={tab === 'products' ? 'active' : ''} onClick={() => setTab('products')}>Товары <span>{products.length}</span></button>
        <button type="button" className={tab === 'categories' ? 'active' : ''} onClick={() => setTab('categories')}>Категории <span>{categories.length}</span></button>
      </div>

      {notice && <div className="form-success" role="status">{notice}</div>}
      {error && !loading && <div className="form-error" role="alert">{error}</div>}
      {loading && <LoadingState label="Загружаем панель…" />}
      {!loading && error && products.length === 0 && categories.length === 0 && <ErrorState message={error} onRetry={loadData} />}

      {!loading && tab === 'products' && (
        <div className="admin-grid">
          <form className="admin-form" onSubmit={handleProductSubmit}>
            <div className="admin-form__heading"><span>Новый товар</span><h2>Добавить в каталог</h2></div>
            <label className="field"><span>Название</span><input value={productName} onChange={(event) => setProductName(event.target.value)} minLength={1} maxLength={200} required /></label>
            <label className="field"><span>Описание</span><textarea value={productDescription} onChange={(event) => setProductDescription(event.target.value)} maxLength={1000} rows={4} /></label>
            <div className="form-row">
              <label className="field"><span>Цена, ₸</span><input type="number" min="0" step="0.01" value={productPrice} onChange={(event) => setProductPrice(event.target.value)} required /></label>
              <label className="field"><span>Остаток</span><input type="number" min="0" step="1" value={productStock} onChange={(event) => setProductStock(event.target.value)} required /></label>
            </div>
            <label className="field"><span>Категория</span><select value={productCategory} onChange={(event) => setProductCategory(event.target.value)}><option value="">Без категории</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select></label>
            <button className="button button--primary button--wide" type="submit" disabled={submitting}>{submitting ? 'Сохраняем…' : 'Создать товар'}</button>
          </form>

          <div className="admin-list">
            <div className="admin-list__heading"><h2>Товары</h2><span>{products.length} позиций</span></div>
            {products.length === 0 && <p className="muted">Товаров пока нет.</p>}
            {products.map((product) => (
              <article className="admin-row" key={product.id}>
                <div className="admin-row__index">{String(product.id).padStart(2, '0')}</div>
                <div className="admin-row__body"><strong>{product.name}</strong><span>{product.category_id ? categoryNames.get(product.category_id) ?? 'Без категории' : 'Без категории'} · Остаток {product.stock}</span></div>
                <strong>{formatPrice(product.price)}</strong>
              </article>
            ))}
          </div>
        </div>
      )}

      {!loading && tab === 'categories' && (
        <div className="admin-grid">
          <form className="admin-form" onSubmit={handleCategorySubmit}>
            <div className="admin-form__heading"><span>{editingCategory ? 'Редактирование' : 'Новая категория'}</span><h2>{editingCategory ? editingCategory.name : 'Добавить раздел'}</h2></div>
            <label className="field"><span>Название</span><input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} minLength={1} maxLength={100} required /></label>
            <label className="field"><span>Описание</span><textarea value={categoryDescription} onChange={(event) => setCategoryDescription(event.target.value)} maxLength={500} rows={4} /></label>
            <button className="button button--primary button--wide" type="submit" disabled={submitting}>{submitting ? 'Сохраняем…' : editingCategory ? 'Сохранить изменения' : 'Создать категорию'}</button>
            {editingCategory && <button className="button button--ghost button--wide" type="button" onClick={cancelCategoryEdit}>Отмена</button>}
          </form>

          <div className="admin-list">
            <div className="admin-list__heading"><h2>Категории</h2><span>{categories.length} разделов</span></div>
            {categories.length === 0 && <p className="muted">Категорий пока нет.</p>}
            {categories.map((category) => (
              <article className="admin-row admin-row--actions" key={category.id}>
                <div className="admin-row__index">{String(category.id).padStart(2, '0')}</div>
                <div className="admin-row__body"><strong>{category.name}</strong><span>{category.description ?? 'Без описания'}</span></div>
                <div className="row-actions">
                  <button type="button" onClick={() => startCategoryEdit(category)}>Изменить</button>
                  <button type="button" className="danger" onClick={() => void deleteCategory(category)}>Удалить</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
