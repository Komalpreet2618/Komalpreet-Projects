const userService = require("../services/userService");

const getAssignableUsers = async (req, res) => {
  try {
    const users = await userService.getAssignableUsers();

    return res.status(200).json({
      users,
    });
  } catch (error) {
    console.error("Failed to fetch assignable users:", error.message);

    return res.status(500).json({
      message: "Failed to fetch assignable users",
    });
  }
};

module.exports = {
  getAssignableUsers,
};