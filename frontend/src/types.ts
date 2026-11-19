export type UserRole = 'customer' | 'admin'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  created_at: string
}

export interface AuthToken {
  access_token: string
  token_type: 'bearer'
}

export interface Product {
  id: number
  name: string
  description: string | null
  price: string | number
  stock: number
  category_id: number | null
  image_url: string | null
  is_active: boolean
}

export interface PaginatedProducts {
  items: Product[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface Category {
  id: number
  name: string
  description: string | null
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface ProductPayload {
  name: string
  description: string | null
  price: string
  stock: number
  category_id: number | null
  image_url?: string | null
  is_active?: boolean
}
