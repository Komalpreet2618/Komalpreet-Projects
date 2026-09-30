const express = require("express");

const router = express.Router();

const {
  authenticateToken,
} = require("../middleware/authMiddleware");

const issueCommentController = require("../controllers/issueCommentController");

// Create a comment
router.post(
  "/:issueId/comments",
  authenticateToken,
  issueCommentController.createComment
);

// Get all comments for an issue
router.get(
  "/:issueId/comments",
  authenticateToken,
  issueCommentController.getComments
);

module.exports = router;