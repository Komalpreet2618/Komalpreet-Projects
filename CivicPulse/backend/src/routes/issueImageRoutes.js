const express = require("express");
const multer = require("multer");

const router = express.Router();

const {
  authenticateToken,
} = require("../middleware/authMiddleware");

const upload = require("../middleware/uploadMiddleware");

const issueImageController = require("../controllers/issueImageController");

router.post(
  "/:issueId/images",
  authenticateToken,
  upload.array("images", 5),
  issueImageController.uploadIssueImage
);

router.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    return res.status(400).json({
      message: error.message,
    });
  }

  if (error) {
    return res.status(400).json({
      message: error.message,
    });
  }

  next();
});

router.get(
  "/:issueId/images",
  issueImageController.getIssueImages
);

router.delete(
  "/images/:imageId",
  authenticateToken,
  issueImageController.deleteIssueImage
);

module.exports = router;