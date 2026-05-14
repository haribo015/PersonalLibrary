// Partial update contract for inline edits and the full edit form.
export interface LibraryUpdate {
  category?: string;
  reading_status?: string;
  priority?: string;
  source?: string;
  reading_format?: string;
  pages_total?: number | null;
  pages_read?: number | null;
  started_at?: string | null;
  finished_at?: string | null;
  last_opened_at?: string | null;
  personal_notes?: string | null;
  favorite?: boolean | null;
  tags?: string | null;
}
