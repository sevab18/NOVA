import type {
  AuthToken,
  Category,
  LoginPayload,
  PaginatedProducts,
  Product,
  ProductPayload,
  RegisterPayload,
  User,
} from '../types'


const API_URL = (
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api/v1'
).replace(/\/$/, '')

export const TOKEN_STORAGE_KEY = 'nova-store-access-token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function errorMessage(payload: unknown): string {
  if (!payload || typeof payload !== 'object' || !('detail' in payload)) {
    return 'Не удалось выполнить запрос'
  }

  const detail = payload.detail
  if (typeof detail === 'string') return detail

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String(item.msg)
        }
        return 'Проверьте введённые данные'
      })
      .join('. ')
  }

  return 'Не удалось выполнить запрос'
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body) headers.set('Content-Type', 'application/json')

  const accessToken = token ?? sessionStorage.getItem(TOKEN_STORAGE_KEY)
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new ApiError(response.status, errorMessage(payload))
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  register: (payload: RegisterPayload) =>
    request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  login: (payload: LoginPayload) =>
    request<AuthToken>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  me: (token?: string | null) => request<User>('/users/me', {}, token),

  products: () => request<PaginatedProducts>('/products?page_size=100'),
  product: (productId: number) => request<Product>(`/products/${productId}`),
  createProduct: (payload: ProductPayload) =>
    request<Product>('/products', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  categories: () => request<Category[]>('/categories'),
  createCategory: (payload: { name: string; description: string | null }) =>
    request<Category>('/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateCategory: (
    categoryId: number,
    payload: { name?: string; description?: string | null },
  ) =>
    request<Category>(`/categories/${categoryId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteCategory: (categoryId: number) =>
    request<void>(`/categories/${categoryId}`, { method: 'DELETE' }),
}
