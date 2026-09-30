const express = require("express");

const router = express.Router();

const {
  authenticateToken,
  authorizeRoles,
} = require("../middleware/authMiddleware");

const issueAssignmentController = require("../controllers/issueAssignmentController");

// Create an assignment
router.post(
  "/:issueId/assignments",
  authenticateToken,
  authorizeRoles("admin", "authority"),
  issueAssignmentController.createAssignment
);

// Get assignment history
router.get(
  "/:issueId/assignments",
  authenticateToken,
  issueAssignmentController.getAssignments
);

module.exports = router;