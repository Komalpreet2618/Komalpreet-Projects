const express = require("express");
const cors = require("cors");

const authRoutes = require("./routes/authRoutes");
const userRoutes = require("./routes/userRoutes");
const issueRoutes = require("./routes/issueRoutes");
const issueImageRoutes = require("./routes/issueImageRoutes");
const issueCommentRoutes = require("./routes/issueCommentRoutes");
const issueAssignmentRoutes = require("./routes/issueAssignmentRoutes");

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

app.use("/uploads", express.static("uploads"));

app.use("/api/issues", issueImageRoutes);
app.use("/api/issues", issueCommentRoutes);
app.use("/api/issues", issueAssignmentRoutes);

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);
app.use("/api/issues", issueRoutes);

// Test route
app.get("/", (req, res) => {
  res.json({
    message: "CivicPulse Backend is Running!",
  });
});

module.exports = app;