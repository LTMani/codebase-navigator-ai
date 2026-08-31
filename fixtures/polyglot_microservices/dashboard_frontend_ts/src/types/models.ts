export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  role: 'ADMIN' | 'DEVELOPER' | 'VIEWER' | 'AUDITOR';
  isActive: boolean;
  isMfaEnabled: boolean;
}

export interface PaymentRecord {
  id: string;
  customerId: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'AUTHORIZED' | 'CAPTURED' | 'FAILED' | 'REFUNDED';
  createdAt: string;
}

export interface ProductInventoryItem {
  id: string;
  sku: string;
  name: string;
  category: string;
  unitPrice: number;
  reorderThreshold: number;
  quantityAvailable: number;
  quantityReserved: number;
}

export interface MetricSummary {
  metricName: string;
  currentValue: number;
  previousValue: number;
  changePercentage: number;
  trend: 'up' | 'down' | 'neutral';
}
