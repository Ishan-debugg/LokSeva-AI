const pool = require("../config/db");

function toIST(date) {
  return new Date(date).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

async function checkSLA() {
  const now = new Date();

  const breached = await pool.query(
    `SELECT * FROM complaints
     WHERE status != 'resolved' AND deadline < $1 AND sla_status != 'breached'`,
    [now]
  );
  for (let c of breached.rows) {
    console.log(`🚨 SLA BREACH: #${c.id} — deadline was ${toIST(c.deadline)}`);
    await pool.query(`UPDATE complaints SET sla_status='breached' WHERE id=$1`, [c.id]);
  }

  const atRisk = await pool.query(
    `SELECT * FROM complaints
     WHERE status != 'resolved'
     AND deadline > $1
     AND deadline <= $1 + INTERVAL '24 hours'
     AND sla_status != 'at_risk'`,
    [now]
  );
  for (let c of atRisk.rows) {
    console.log(`AT RISK: #${c.id} — due ${toIST(c.deadline)}`);
    await pool.query(`UPDATE complaints SET sla_status='at_risk' WHERE id=$1`, [c.id]);
  }

  const toEscalate = await pool.query(
    `SELECT * FROM complaints
     WHERE status = 'pending'
     AND created_at < NOW() - INTERVAL '7 days'
     AND escalated = false`
  );
  for (let c of toEscalate.rows) {
    console.log(`⬆ Escalating #${c.id}`);
    await pool.query(
      `UPDATE complaints SET escalated=true, sla_status='breached' WHERE id=$1`,
      [c.id]
    );
  }

  console.log(`✅SLA check [${toIST(now)}] — ${breached.rows.length} breached, ${atRisk.rows.length} at risk, ${toEscalate.rows.length} escalated`);
}

async function getSLASummary() {
  const result = await pool.query(`
    SELECT
      department,
      COUNT(*) AS total,
      COUNT(*) FILTER (WHERE status = 'resolved') AS resolved,
      COUNT(*) FILTER (WHERE status != 'resolved') AS active,
      COUNT(*) FILTER (
        WHERE status != 'resolved' AND deadline > NOW() + INTERVAL '24 hours'
      ) AS on_track,
      COUNT(*) FILTER (
        WHERE status != 'resolved'
        AND deadline <= NOW() + INTERVAL '24 hours'
        AND deadline > NOW()
      ) AS at_risk,
      COUNT(*) FILTER (
        WHERE status != 'resolved' AND deadline <= NOW()
      ) AS breached,
      ROUND(
        100.0 * COUNT(*) FILTER (
          WHERE status = 'resolved'
          AND updated_at IS NOT NULL
          AND updated_at <= deadline
        ) / NULLIF(COUNT(*), 0), 1
      ) AS compliance_pct
    FROM complaints
    GROUP BY department
    ORDER BY breached DESC
  `);
  return result.rows;
}

async function getSLAAlerts() {
  const result = await pool.query(`
    SELECT
      id, complaint_text, department, priority, deadline, created_at,
      CASE
        WHEN deadline <= NOW() THEN 'breached'
        WHEN deadline <= NOW() + INTERVAL '24 hours' THEN 'at_risk'
        ELSE 'on_track'
      END AS sla_status
    FROM complaints
    WHERE status != 'resolved'
    AND deadline <= NOW() + INTERVAL '24 hours'
    ORDER BY deadline ASC
    LIMIT 50
  `);
  return result.rows;
}

module.exports = { checkSLA, getSLASummary, getSLAAlerts };