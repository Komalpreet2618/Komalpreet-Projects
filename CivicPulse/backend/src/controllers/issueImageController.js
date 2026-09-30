const issueImageService = require("../services/issueImageService");

const uploadIssueImage = async (req, res) => {
  try {
    const { issueId } = req.params;

    if (!req.files || req.files.length === 0) {
  return res.status(400).json({
    message: "At least one image file is required",
  });
}

const images = [];

for (const file of req.files) {
  const imageUrl = `/${file.path.replace(/\\/g, "/")}`;

  const image = await issueImageService.addIssueImage(
    issueId,
    imageUrl
  );

  images.push(image);
}

return res.status(201).json({
  message: "Images uploaded successfully",
  count: images.length,
  images,
});
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: "Issue not found",
      });
    }

    console.error("Upload issue image error:", error);

    return res.status(500).json({
      message: "Failed to upload image",
    });
  }
};

const getIssueImages = async (req, res) => {
  try {
    const { issueId } = req.params;

    const images = await issueImageService.getIssueImages(issueId);

    return res.status(200).json({
      message: "Issue images retrieved successfully",
      count: images.length,
      images,
    });
  } catch (error) {
    if (error.message === "Issue not found") {
      return res.status(404).json({
        message: "Issue not found",
      });
    }

    console.error("Get issue images error:", error);

    return res.status(500).json({
      message: "Failed to retrieve issue images",
    });
  }
};

const deleteIssueImage = async (req, res) => {
  try {
    const { imageId } = req.params;

    const deletedImage =
  await issueImageService.deleteIssueImage(
    imageId,
    req.user.id,
    req.user.role
  );

    return res.status(200).json({
      message: "Image deleted successfully",
      image: deletedImage,
    });
  } catch (error) {
    if (error.message === "Image not found") {
      return res.status(404).json({
        message: "Image not found",
      });
    }

    console.error("Delete issue image error:", error);

    return res.status(500).json({
      message: "Failed to delete issue image",
    });
  }
};

module.exports = {
  uploadIssueImage,
  getIssueImages,
  deleteIssueImage,
};