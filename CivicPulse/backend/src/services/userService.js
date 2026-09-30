const userModel = require("../models/userModel");

const getAssignableUsers = async () => {
  return await userModel.getAssignableUsers();
};

module.exports = {
  getAssignableUsers,
};