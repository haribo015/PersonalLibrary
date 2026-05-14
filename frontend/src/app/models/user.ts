// Authenticated user projection; sensitive fields are intentionally absent.
export interface User {
  id: number;
  name: string;
  email: string;
  reading_goal?: number;
  role?: string;
}
