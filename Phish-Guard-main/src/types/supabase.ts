export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      scans: {
        Row: {
          created_at: string
          id: string
          severity: 'low' | 'medium' | 'high'
          url: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          severity: 'low' | 'medium' | 'high'
          url: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          severity?: 'low' | 'medium' | 'high'
          url?: string
          user_id?: string
        }
      }
    }
  }
}