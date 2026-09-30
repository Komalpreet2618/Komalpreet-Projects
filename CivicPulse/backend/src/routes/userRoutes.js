const express = require("express");

const userController = require("../controllers/userController");

const {
  authenticateToken,
  authorizeRoles,
} = require("../middleware/authMiddleware");

const router = express.Router();

router.get(
  "/assignable",
  authenticateToken,
  authorizeRoles("admin", "authority"),
  userController.getAssignableUsers
);

module.exports = router;