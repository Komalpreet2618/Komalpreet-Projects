const issueModel = require("../models/issueModel");
const issueUpdateModel = require("../models/issueUpdateModel");

const createIssue = async (issueData, reportedBy) => {
  const {
    title,
    description,
    category,
    priority,
    latitude,
    longitude,
    address,
  } = issueData;

  if (
    !title ||
    !description ||
    !category ||
    !priority ||
    latitude === undefined ||
    longitude === undefined
  ) {
    throw new Error("All required issue fields must be provided");
  }

  const issue = await issueModel.createIssue(
    title,
    description,
    category,
    priority,
    latitude,
    longitude,
    address,
    reportedBy
  );

  return issue;
};

const getAllIssues = async () => {
  const issues = await issueModel.getAllIssues();

  return issues;
};

const getIssuesByUser = async (userId) => {
  const issues = await issueModel.getIssuesByUser(userId);

  return issues;
};

const getIssueById = async (id) => {
  const issue = await issueModel.getIssueById(id);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return issue;
};

const updateIssueStatus = async (
  issueId,
  newStatus,
  updatedBy,
  comment
) => {
  // Get the current issue
  const existingIssue = await issueModel.getIssueById(issueId);

  if (!existingIssue) {
    throw new Error("Issue not found");
  }

  const previousStatus = existingIssue.status;

  // Define allowed status transitions
  const allowedTransitions = {
    reported: ["under_review", "rejected"],
    under_review: ["assigned", "rejected"],
    assigned: ["in_progress"],
    in_progress: ["resolved"],
    resolved: [],
    rejected: [],
  };

  // Check whether the requested transition is allowed
  if (!allowedTransitions[previousStatus].includes(newStatus)) {
    throw new Error(
      `Cannot change issue status from ${previousStatus} to ${newStatus}`
    );
  }

  // Update the issue status
  const updatedIssue = await issueModel.updateIssueStatus(
    issueId,
    newStatus
  );

  // Save the status change in issue history
  await issueUpdateModel.createIssueUpdate(
    issueId,
    updatedBy,
    previousStatus,
    newStatus,
    comment
  );

  return updatedIssue;
};

const getIssueHistory = async (issueId) => {
  // Check whether the issue exists
  const existingIssue = await issueModel.getIssueById(issueId);

  if (!existingIssue) {
    throw new Error("Issue not found");
  }

  const history = await issueUpdateModel.getIssueUpdates(issueId);

  return history;
};

module.exports = {
  createIssue,
  getAllIssues,
  getIssuesByUser,
  getIssueById,
  updateIssueStatus,
  getIssueHistory,
};