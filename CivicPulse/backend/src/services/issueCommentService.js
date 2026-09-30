const issueCommentModel = require("../models/issueCommentModel");
const issueModel = require("../models/issueModel");

const addComment = async (issueId, userId, comment) => {
  // Make sure the issue exists
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return await issueCommentModel.createComment(
    issueId,
    userId,
    comment
  );
};

const getComments = async (issueId) => {
  // Make sure the issue exists
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return await issueCommentModel.getCommentsByIssueId(issueId);
};

module.exports = {
  addComment,
  getComments,
};