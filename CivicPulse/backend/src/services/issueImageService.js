const fs = require("fs");

const issueImageModel = require("../models/issueImageModel");
const issueModel = require("../models/issueModel");


const addIssueImage = async (issueId, imageUrl) => {
  // Check whether the issue exists
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return await issueImageModel.createIssueImage(
    issueId,
    imageUrl
  );
};

const getIssueImages = async (issueId) => {
  // Check whether the issue exists
  const issue = await issueModel.getIssueById(issueId);

  if (!issue) {
    throw new Error("Issue not found");
  }

  return await issueImageModel.getIssueImages(issueId);
};

const deleteIssueImage = async (imageId, userId, userRole) => {
  const image = await issueImageModel.getIssueImageById(imageId);

  if (!image) {
    throw new Error("Image not found");
  }

  const issue = await issueModel.getIssueById(image.issue_id);

  if (!issue) {
    throw new Error("Issue not found");
  }

  const isOwner = issue.reported_by === userId;
  const isAuthorizedRole =
    userRole === "admin" || userRole === "authority";

  if (!isOwner && !isAuthorizedRole) {
    throw new Error("You do not have permission to delete this image");
  }

  const deletedImage =
    await issueImageModel.deleteIssueImage(imageId);

  const imagePath = deletedImage.image_url.replace(/\\/g, "/");

  if (fs.existsSync(imagePath)) {
    fs.unlinkSync(imagePath);
  }

  return deletedImage;
};

module.exports = {
  addIssueImage,
  getIssueImages,
  deleteIssueImage,
};