import { Link } from 'react-router-dom'

import type { Product } from '../types'
import { formatPrice } from '../utils/format'
import { ArrowIcon } from './Icons'
import { ProductVisual } from './ProductVisual'


export function ProductCard({
  product,
  categoryName,
}: {
  product: Product
  categoryName?: string
}) {
  return (
    <article className="product-card">
      <Link to={`/products/${product.id}`} className="product-card__visual" aria-label={`Открыть ${product.name}`}>
        <ProductVisual productId={product.id} name={product.name} />
      </Link>
      <div className="product-card__body">
        <div className="product-card__meta">
          <span>{categoryName ?? 'Без категории'}</span>
          <span className={product.stock > 0 ? 'stock stock--available' : 'stock stock--empty'}>
            {product.stock > 0 ? `В наличии: ${product.stock}` : 'Нет в наличии'}
          </span>
        </div>
        <h3><Link to={`/products/${product.id}`}>{product.name}</Link></h3>
        <div className="product-card__footer">
          <strong>{formatPrice(product.price)}</strong>
          <Link to={`/products/${product.id}`} className="round-link" aria-label="Подробнее">
            <ArrowIcon />
          </Link>
        </div>
      </div>
    </article>
  )
}
