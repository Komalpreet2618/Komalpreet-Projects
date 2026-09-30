const pool = require("../config/db");

const issueAssignmentModel = require("../models/issueAssignmentModel");
const issueModel = require("../models/issueModel");
const userModel = require("../models/userModel");

const addAssignment = async (
  issueId,
  assignedTo,
  assignedBy,
  note
) => {
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  if (issue.status !== "under_review") {
    throw new Error(
      "Issue can only be assigned when it is under review"
    );
  }

  const assignedUser = await userModel.findUserById(assignedTo);

  if (!assignedUser) {
    throw new Error("Assigned user not found");
  }

  if (
    assignedUser.role !== "authority" &&
    assignedUser.role !== "admin"
  ) {
    throw new Error(
      "Issues can only be assigned to authority or admin users"
    );
  }

  const client = await pool.connect();

  try {
    await client.query("BEGIN");

    const assignmentQuery = `
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

    const assignmentResult = await client.query(
      assignmentQuery,
      [issueId, assignedTo, assignedBy, note || null]
    );

    const updatedIssue =
      await issueModel.updateIssueStatusWithClient(
        client,
        issueId,
        "assigned"
      );

    const historyQuery = `
      INSERT INTO issue_updates (
        issue_id,
        updated_by,
        previous_status,
        new_status,
        comment
      )
      VALUES ($1, $2, $3, $4, $5);
    `;

    await client.query(historyQuery, [
      issueId,
      assignedBy,
      "under_review",
      "assigned",
      note || "Issue assigned successfully.",
    ]);

    await client.query("COMMIT");

    return {
      assignment: assignmentResult.rows[0],
      issue: updatedIssue,
    };
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
};

const getAssignments = async (issueId) => {
  // Check that the issue exists
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return await issueAssignmentModel.getAssignmentsByIssueId(
    issueId
  );
};

module.exports = {
  addAssignment,
  getAssignments,
};