const pool = require("../config/db");

const createAssignment = async (
  issueId,
  assignedTo,
  assignedBy,
  note
) => {
  const query = `
    INSERT INTO issue_assignments (
      issue_id,
      assigned_to,
      assigned_by,
      note
    )
    VALUES ($1, $2, $3, $4)
    RETURNING
      id,
      issue_id,
      assigned_to,
      assigned_by,
      assigned_at,
      note;
  `;

  const result = await pool.query(query, [
    issueId,
    assignedTo,
    assignedBy,
    note || null,
  ]);

  return result.rows[0];
};

const getAssignmentsByIssueId = async (issueId) => {
  const query = `
    SELECT
      ia.id,
      ia.issue_id,
      ia.assigned_to,
      assigned_user.name AS assigned_to_name,
      assigned_user.role AS assigned_to_role,
      ia.assigned_by,
      assigning_user.name AS assigned_by_name,
      assigning_user.role AS assigned_by_role,
      ia.assigned_at,
      ia.note
    FROM issue_assignments ia
    JOIN users assigned_user
      ON ia.assigned_to = assigned_user.id
    JOIN users assigning_user
      ON ia.assigned_by = assigning_user.id
    WHERE ia.issue_id = $1
    ORDER BY ia.assigned_at ASC;
  `;

  const result = await pool.query(query, [issueId]);

  return result.rows;
};

module.exports = {
  createAssignment,
  getAssignmentsByIssueId,
};