const issueService = require("../services/issueService");

const createIssue = async (req, res) => {
  try {
    const reportedBy = req.user.userId;

    const issue = await issueService.createIssue(
      req.body,
      reportedBy
    );

    res.status(201).json({
      message: "Issue reported successfully",
      issue,
    });
  } catch (error) {
    res.status(400).json({
      message: error.message,
    });
  }
};

const getAllIssues = async (req, res) => {
  try {
    const issues = await issueService.getAllIssues();

    res.status(200).json({
      message: "Issues retrieved successfully",
      count: issues.length,
      issues,
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to retrieve issues",
      error: error.message,
    });
  }
};

const getMyIssues = async (req, res) => {
  try {
    const userId = req.user.userId;

    const issues = await issueService.getIssuesByUser(userId);

    res.status(200).json({
      message: "Your issues retrieved successfully",
      count: issues.length,
      issues,
    });
  } catch (error) {
    console.error("Get my issues error:", error.message);

    res.status(500).json({
      message: "Failed to retrieve your issues",
    });
  }
};

const getIssueById = async (req, res) => {
  try {
    const { id } = req.params;

    const issue = await issueService.getIssueById(id);

    res.status(200).json({
      message: "Issue retrieved successfully",
      issue,
    });
  } catch (error) {
    res.status(404).json({
      message: error.message,
    });
  }
};

const updateIssueStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status, comment } = req.body;

    const updatedBy = req.user.userId;

    const updatedIssue = await issueService.updateIssueStatus(
      id,
      status,
      updatedBy,
      comment
    );

    res.status(200).json({
      message: "Issue status updated successfully",
      issue: updatedIssue,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: error.message,
      });
    }

    res.status(400).json({
      message: error.message,
    });
  }
};

const getIssueHistory = async (req, res) => {
  try {
    const { id } = req.params;

    const history = await issueService.getIssueHistory(id);

    res.status(200).json({
      message: "Issue history retrieved successfully",
      count: history.length,
      history,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: error.message,
      });
    }

    res.status(500).json({
      message: "Failed to retrieve issue history",
    });
  }
};

module.exports = {
  createIssue,
  getAllIssues,
  getMyIssues,
  getIssueById,
  updateIssueStatus,
  getIssueHistory
};