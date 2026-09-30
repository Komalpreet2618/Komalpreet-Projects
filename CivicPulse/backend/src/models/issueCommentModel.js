const pool = require("../config/db");

const createComment = async (issueId, userId, comment) => {
  const query = `
    INSERT INTO issue_comments (
      issue_id,
      commented_by,
      comment
    )
    VALUES ($1, $2, $3)
    RETURNING
      id,
      issue_id,
      commented_by,
      comment,
      created_at;
  `;

  const result = await pool.query(query, [
    issueId,
    userId,
    comment,
  ]);

  return result.rows[0];
};

const getCommentsByIssueId = async (issueId) => {
  const query = `
    SELECT
      ic.id,
      ic.issue_id,
      ic.commented_by,
      u.name AS commented_by_name,
      u.role AS commented_by_role,
      ic.comment,
      ic.created_at
    FROM issue_comments ic
    JOIN users u
      ON ic.commented_by = u.id
    WHERE ic.issue_id = $1
    ORDER BY ic.created_at ASC;
  `;

  const result = await pool.query(query, [issueId]);

  return result.rows;
};

module.exports = {
  createComment,
  getCommentsByIssueId,
};