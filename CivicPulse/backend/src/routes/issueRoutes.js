const express = require("express");

const issueController = require("../controllers/issueController");
const {
  authenticateToken,
  authorizeRoles,
} = require("../middleware/authMiddleware");

const router = express.Router();

router.post("/", authenticateToken, issueController.createIssue);

router.get(
  "/my",
  authenticateToken,
  issueController.getMyIssues
);

router.get(
  "/",
  authenticateToken,
  authorizeRoles("admin", "authority"),
  issueController.getAllIssues
);

router.patch(
  "/:id/status",
  authenticateToken,
  authorizeRoles("admin", "authority"),
  issueController.updateIssueStatus
);

router.get("/:id/history", issueController.getIssueHistory);

router.get("/:id", issueController.getIssueById);

module.exports = router;