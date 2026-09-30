const issueAssignmentService = require("../services/issueAssignmentService");

const createAssignment = async (req, res) => {
  try {
    const { issueId } = req.params;
    const { assignedTo, note } = req.body;

    if (!assignedTo) {
      return res.status(400).json({
        message: "assignedTo is required",
      });
    }

    const assignment = await issueAssignmentService.addAssignment(
      issueId,
      assignedTo,
      req.user.userId,
      note
    );

    return res.status(201).json({
     message: "Issue assigned successfully",
     assignment: assignment.assignment,
     issue: assignment.issue,
   });
  } catch (error) {
    if (
      error.message === "Issue not found" ||
      error.message === "Assigned user not found"
    ) {
      return res.status(404).json({
        message: error.message,
      });
    }

    if (
      error.message ===
    "Issues can only be assigned to authority or admin users" ||
      error.message ===
    "Issue can only be assigned when it is under review"
    ) {
      return res.status(400).json({
       message: error.message,
      });
    }

    console.error("Create assignment error:", error);

    return res.status(500).json({
      message: "Failed to assign issue",
    });
  }
};

const getAssignments = async (req, res) => {
  try {
    const { issueId } = req.params;

    const assignments =
      await issueAssignmentService.getAssignments(issueId);

    return res.status(200).json({
      message: "Assignments retrieved successfully",
      count: assignments.length,
      assignments,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: error.message,
      });
    }

    console.error("Get assignments error:", error);

    return res.status(500).json({
      message: "Failed to retrieve assignments",
    });
  }
};

module.exports = {
  createAssignment,
  getAssignments,
};