export interface ReceiptData {
  merchant_name: string;
  date: string;
  total_amount: number;
  tax_amount?: number;
  items?: ReceiptItem[];
  [key: string]: unknown;
}

export interface ReceiptItem {
  name: string;
  quantity: number;
  price: number;
  [key: string]: unknown;
}

export interface TransactionData {
  id: string;
  user_id: string;
  merchant_name: string;
  amount: number;
  category: string;
  transaction_date: string;
  [key: string]: unknown;
}

export interface UploadReceiptResponse {
  success: boolean;
  message: string;
  data: {
    file_path: string;
    extracted_data: ReceiptData;
    transaction: TransactionData;
  };
}

export interface UploadReceiptRequest {
  file: File;
  user_id: string;
  category_name?: string;
}
