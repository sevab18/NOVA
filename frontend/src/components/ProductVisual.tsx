export function ProductVisual({
  productId,
  name,
  large = false,
}: {
  productId: number
  name: string
  large?: boolean
}) {
  const tone = (productId % 4) + 1
  const initials = name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  return (
    <div className={`product-visual product-visual--${tone}${large ? ' product-visual--large' : ''}`}>
      <span className="product-visual__shape" aria-hidden="true" />
      <span className="product-visual__monogram">{initials || 'N'}</span>
      <span className="product-visual__label">NOVA SELECT</span>
    </div>
  )
}
