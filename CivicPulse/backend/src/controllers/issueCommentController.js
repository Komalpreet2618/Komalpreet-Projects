const issueCommentService = require("../services/issueCommentService");

const createComment = async (req, res) => {
  try {
    const { issueId } = req.params;
    const { comment } = req.body;

    if (!comment || !comment.trim()) {
      return res.status(400).json({
        message: "Comment is required",
      });
    }

    const newComment = await issueCommentService.addComment(
      issueId,
      req.user.userId,
      comment.trim()
    );

    return res.status(201).json({
      message: "Comment added successfully",
      comment: newComment,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: error.message,
      });
    }

    console.error("Create comment error:", error);

    return res.status(500).json({
      message: "Failed to add comment",
    });
  }
};

const getComments = async (req, res) => {
  try {
    const { issueId } = req.params;

    const comments = await issueCommentService.getComments(issueId);

    return res.status(200).json({
      message: "Comments retrieved successfully",
      count: comments.length,
      comments,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: error.message,
      });
    }

    console.error("Get comments error:", error);

    return res.status(500).json({
      message: "Failed to retrieve comments",
    });
  }
};

module.exports = {
  createComment,
  getComments,
};