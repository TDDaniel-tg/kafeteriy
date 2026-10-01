const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  middle_name: string;
  full_name: string;
  role: 'employee' | 'maternity' | 'vip' | 'hr' | 'admin' | 'exclusion';
  department: string;
  grade: string;
  hire_date?: string;
  birth_date?: string;
  gender: string;
  city: string;
  delivery_address: string;
  segment: string;
  is_frozen: boolean;
  has_unspent_main_vacation: boolean;
  flexible_schedule_active: boolean;
  onboarding_completed: boolean;
  totp_enabled: boolean;
  available_balance: number;
  total_balance: number;
  sections_visibility?: Record<string, boolean>;
  unread_notifications?: number;
}

export interface ProductItem {
  id: number | string;
  slug?: string;
  name: string;
  category: string;
  supplier: string;
  price: number;
  image: string;
  tag?: string;
  product_type: string;
  description: string;
  terms?: string;
  is_general_offer?: boolean;
  is_active?: boolean;
  is_archived?: boolean;
  requires_approval?: boolean;
}

export interface OrderRow {
  id: number | string;
  order_number: string;
  name?: string;
  status: string;
  status_display?: string;
  total_points: number;
  created_at: string;
  recipient_name?: string;
  can_cancel?: boolean;
  items?: Array<{
    id: number;
    product: ProductItem;
    price: number;
    quantity: number;
    subtotal: number;
  }>;
}

export interface PointsBalanceData {
  total_balance: number;
  available_balance: number;
  frozen_balance: number;
  burnable_amount: number;
  burnable_expires_at?: string;
  non_burnable_amount: number;
  point_ruble_rate: number;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    let errorDetail = `Request failed: ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.error || errJson.detail || JSON.stringify(errJson);
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  // If status is 204 or empty
  const text = await response.text();
  return text ? JSON.parse(text) : ({} as T);
}

export const api = {
  // Auth
  getMe: () => request<UserProfile>('/auth/me/'),
  login: (username: string, password?: string) => request<UserProfile>('/auth/login/', { method: 'POST', body: JSON.stringify({ username, password }) }),
  logout: () => request<{ message: string }>('/auth/logout/', { method: 'POST' }),
  switchRole: (role: string) => request<UserProfile>('/auth/switch-role/', { method: 'POST', body: JSON.stringify({ role }) }),
  setup2FA: () => request<{ secret: string; totp_uri: string }>('/auth/setup-2fa/', { method: 'POST' }),
  verify2FA: (code: string) => request<{ success: boolean; message: string }>('/auth/verify-2fa/', { method: 'POST', body: JSON.stringify({ code }) }),

  // Catalog
  getCatalog: (params?: { category?: string; search?: string; sort?: string }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set('category', params.category);
    if (params?.search) q.set('search', params.search);
    if (params?.sort) q.set('sort', params.sort);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<any>(`/catalog/${qs}`);
  },
  createProduct: (data: Partial<ProductItem>) => request<ProductItem>('/catalog/', { method: 'POST', body: JSON.stringify(data) }),
  archiveProduct: (id: string | number) => request<{ success: boolean; message: string }>(`/catalog/${id}/archive/`, { method: 'POST' }),

  // Cart
  getCart: () => request<{ items: any[]; total_price: number; count: number }>('/cart/'),
  addToCart: (productId: number | string, quantity = 1, customData = {}) => request<{ success: boolean; message: string }>('/cart/add/', { method: 'POST', body: JSON.stringify({ product_id: productId, quantity, custom_data: customData }) }),
  removeFromCart: (productId: number | string) => request<{ success: boolean; message: string }>('/cart/remove/', { method: 'POST', body: JSON.stringify({ product_id: productId }) }),
  clearCart: () => request<{ success: boolean; message: string }>('/cart/clear/', { method: 'POST' }),

  // Orders
  getOrders: (params?: { search?: string; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.search) q.set('search', params.search);
    if (params?.status) q.set('status', params.status);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<any>(`/orders/${qs}`);
  },
  checkout: (items?: any[], recipientInfo?: any, deliveryAddress?: string) => request<OrderRow>('/orders/checkout/', { method: 'POST', body: JSON.stringify({ items, recipient_info: recipientInfo, delivery_address: deliveryAddress }) }),
  cancelOrder: (id: number | string, reason?: string) => request<OrderRow>(`/orders/${id}/cancel/`, { method: 'POST', body: JSON.stringify({ reason }) }),
  getApprovals: () => request<any>('/approvals/'),
  decideApproval: (id: number | string, decision: 'approved' | 'rejected', comment = '') => request<any>(`/approvals/${id}/decide/`, { method: 'POST', body: JSON.stringify({ decision, comment }) }),

  // Points & Balances
  getPointsBalance: () => request<PointsBalanceData>('/points/balance/'),
  getPointsHistory: () => request<any[]>('/points/history/'),
  manualAdjust: (userId: number, amount: number, isAdd: boolean, comment: string, totpCode: string) => request<any>('/points/manual-adjust/', { method: 'POST', body: JSON.stringify({ user_id: userId, amount, is_add: isAdd, comment, totp_code: totpCode }) }),
  freezeAccount: (userId: number, isFrozen: boolean, comment?: string) => request<any>('/points/freeze/', { method: 'POST', body: JSON.stringify({ user_id: userId, is_frozen: isFrozen, comment }) }),
  transferPoints: (receiverId: number | string, amount: number, comment?: string) => request<any>('/points/transfer/', { method: 'POST', body: JSON.stringify({ receiver_id: receiverId, amount, comment }) }),

  // Health DMS
  getMyDMS: () => request<any>('/health-dms/my-policy/'),
  addFamilyDMS: (data: any) => request<any>('/health-dms/add-family/', { method: 'POST', body: JSON.stringify(data) }),
  optOutDMS: () => request<any>('/health-dms/opt-out/', { method: 'POST' }),

  // Social & Charity
  getCharityFunds: () => request<any[]>('/social/funds/'),
  donateCharity: (fundId: number, amount: number) => request<any>('/social/donate/', { method: 'POST', body: JSON.stringify({ fund_id: fundId, amount }) }),

  // Comms
  getNews: () => request<any[]>('/comms/news/'),
  getBanners: () => request<any[]>('/comms/banners/'),
  getNotifications: () => request<any[]>('/comms/notifications/'),
  markNotificationRead: (id: number) => request<any>(`/comms/notifications/${id}/mark-read/`, { method: 'POST' }),

  // Surveys & Lottery
  getSurveys: () => request<any[]>('/surveys/'),
  submitSurvey: (id: number, answers: any) => request<any>(`/surveys/${id}/submit/`, { method: 'POST', body: JSON.stringify({ answers }) }),
  getLotteries: () => request<any[]>('/surveys/lotteries/'),

  // Support
  getSupportTickets: () => request<any>('/support/tickets/'),
  createSupportTicket: (subject: string, description: string) => request<any>('/support/tickets/', { method: 'POST', body: JSON.stringify({ subject, description }) }),
  suggestPerk: (title: string, description: string, category = '') => request<any>('/support/suggest-perk/', { method: 'POST', body: JSON.stringify({ title, description, category }) }),

  // Admin
  getEmployees: (search?: string) => request<any>(`/employees/${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  sync1C: () => request<any>('/employees/sync_1c/', { method: 'POST' }),
  getAdminSettings: () => request<any[]>('/admin/settings/'),
  updateAdminSetting: (key: string, value: any, comment?: string) => request<any>('/admin/settings/', { method: 'POST', body: JSON.stringify({ key, value, comment }) }),
  getAdminAudit: () => request<any>('/admin/audit/'),
  getAdminAnomalies: () => request<any>('/admin/anomalies/'),
  resolveAnomaly: (ticketId: number, action: 'legitimate' | 'block', comment?: string) => request<any>(`/admin/anomalies/${ticketId}/resolve/`, { method: 'POST', body: JSON.stringify({ action, comment }) }),
  getAdminDashboard: () => request<any>('/admin/analytics/dashboard/'),
  getAccountingExportUrl: () => `${BASE_URL}/admin/analytics/accounting-export/`,
  getPayoutsExportUrl: () => `${BASE_URL}/admin/analytics/payouts-export/`,
  getIntegrations: () => request<any[]>('/admin/integrations/'),
  testIntegration: (id: number) => request<any>(`/admin/integrations/${id}/test/`, { method: 'POST' }),
  getCampaigns: () => request<any>('/campaigns/'),
};
