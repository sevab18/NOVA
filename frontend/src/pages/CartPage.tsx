import { Link } from 'react-router-dom'

import { BagIcon } from '../components/Icons'


export function CartPage() {
  return (
    <section className="container narrow-page placeholder-page">
      <div className="placeholder-icon"><BagIcon size={32} /></div>
      <span className="eyebrow">Спринт 5</span>
      <h1>Корзина — следующий большой модуль</h1>
      <p>Интерфейс подготовлен, но позиции и итоговая цена должны храниться и проверяться на backend. Мы не имитируем покупку только на клиенте.</p>
      <Link to="/catalog" className="button button--primary">Вернуться в каталог</Link>
    </section>
  )
}
