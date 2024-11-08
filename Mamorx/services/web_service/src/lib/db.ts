import { Database } from "sqlite3";
import { open } from "sqlite";
import path from "path";

// Database interface
interface RateLimit {
  session_id: string;
  submissions_count: number;
  last_submission: string;
  last_reset: string;
}

// Initialize database
async function getDb() {
  const db = await open({
    filename: path.join(process.cwd(), "rate-limits.db"),
    driver: Database,
  });

  // Create table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS rate_limits (
      session_id TEXT PRIMARY KEY,
      submissions_count INTEGER DEFAULT 0,
      last_submission DATETIME DEFAULT CURRENT_TIMESTAMP,
      last_reset DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS global_submissions (
      id INTEGER PRIMARY KEY,
      total_count INTEGER DEFAULT 0,
      last_reset DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // Initialize global submissions counter if it doesn't exist
  await db.run(`
    INSERT OR IGNORE INTO global_submissions (id, total_count) VALUES (1, 0);
  `);

  return db;
}

export async function getRateLimitInfo(session_id: string) {
  const db = await getDb();

  // Get or create user rate limit record
  const userLimit = await db.get<RateLimit>(
    "SELECT * FROM rate_limits WHERE session_id = ?",
    [session_id]
  );

  if (!userLimit) {
    await db.run(
      "INSERT INTO rate_limits (session_id, submissions_count) VALUES (?, 0)",
      [session_id]
    );
    return { submissions_count: 0, last_reset: new Date().toISOString() };
  }

  // Check if we need to reset (daily)
  const lastReset = new Date(userLimit.last_reset);
  const now = new Date();
  if (
    now.getDate() !== lastReset.getDate() ||
    now.getMonth() !== lastReset.getMonth()
  ) {
    await db.run(
      "UPDATE rate_limits SET submissions_count = 0, last_reset = CURRENT_TIMESTAMP WHERE session_id = ?",
      [session_id]
    );
    return { submissions_count: 0, last_reset: now.toISOString() };
  }

  return userLimit;
}

export async function incrementSubmissionCount(session_id: string) {
  const db = await getDb();

  // Increment user submission count
  await db.run(
    `
    UPDATE rate_limits 
    SET submissions_count = submissions_count + 1,
        last_submission = CURRENT_TIMESTAMP
    WHERE session_id = ?
  `,
    [session_id]
  );

  // Increment global submission count
  await db.run(`
    UPDATE global_submissions 
    SET total_count = total_count + 1 
    WHERE id = 1
  `);
}

export async function getGlobalSubmissionCount() {
  const db = await getDb();
  const result = await db.get(
    "SELECT total_count FROM global_submissions WHERE id = 1"
  );
  return result?.total_count || 0;
}
