const pool = require("../config/db");

const createIssueUpdate = async (
  issueId,
  updatedBy,
  previousStatus,
  newStatus,
  comment
) => {
  const query = `
    INSERT INTO issue_updates (
      issue_id,
      updated_by,
      previous_status,
      new_status,
      comment
    )
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *;
  `;

  const values = [
    issueId,
    updatedBy,
    previousStatus,
    newStatus,
    comment || null,
  ];

  const result = await pool.query(query, values);

  return result.rows[0];
};

const getIssueUpdates = async (issueId) => {
  const query = `
    SELECT
      iu.id,
      iu.issue_id,
      iu.updated_by,
      u.name AS updated_by_name,
      u.role AS updated_by_role,
      iu.previous_status,
      iu.new_status,
      iu.comment,
      iu.created_at
    FROM issue_updates iu
    JOIN users u
      ON iu.updated_by = u.id
    WHERE iu.issue_id = $1
    ORDER BY iu.created_at ASC;
  `;

  const result = await pool.query(query, [issueId]);

  return result.rows;
};

module.exports = {
  createIssueUpdate,
  getIssueUpdates,
};