import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { Link } from "react-router-dom";
import { apiRequest } from "../services/api";
import "./ManageIssues.css";

function getNextStatuses(currentStatus) {
  const transitions = {
    reported: ["under_review", "rejected"],
    under_review: ["assigned", "rejected"],
    assigned: ["in_progress"],
    in_progress: ["resolved"],
    resolved: [],
    rejected: [],
  };

  return transitions[currentStatus] || [];
}

function formatStatus(status) {
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function ManageIssues() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingIssueId, setUpdatingIssueId] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [assignableUsers, setAssignableUsers] = useState([]);
  const [selectedAssignees, setSelectedAssignees] = useState({});
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("newest");

  useEffect(() => {
    const fetchIssues = async () => {
      try {
        const data = await apiRequest("/api/issues");
        setIssues(data.issues);
      } catch (error) {
        console.error("Failed to fetch issues:", error.message);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchIssues();
  }, []);

  useEffect(() => {
  const fetchAssignableUsers = async () => {
    try {
      const data = await apiRequest("/api/users/assignable");
      setAssignableUsers(data.users);
    } catch (error) {
      console.error(
        "Failed to fetch assignable users:",
        error.message
      );
      setError(error.message);
    }
  };

  fetchAssignableUsers();
}, []);

  const handleStatusUpdate = async (issueId, newStatus) => {
  try {
    setUpdatingIssueId(issueId);
    setError("");
    setSuccessMessage("");

    const data = await apiRequest(`/api/issues/${issueId}/status`, {
      method: "PATCH",
      body: JSON.stringify({
        status: newStatus,
        comment: `Status changed to ${newStatus}`,
      }),
    });

    setIssues((previousIssues) =>
      previousIssues.map((issue) =>
        issue.id === issueId
          ? {
              ...issue,
              status: data.issue.status,
              updated_at: data.issue.updated_at,
            }
          : issue
      )
    );

     setSuccessMessage("Issue status updated successfully.");

  } catch (error) {
    console.error("Failed to update issue status:", error.message);
    setError(error.message);
  } finally {
    setUpdatingIssueId(null);
  }
};

const handleAssignment = async (issueId) => {
  const assignedTo = selectedAssignees[issueId];

  if (!assignedTo) {
    setError("Please select a user before assigning the issue.");
    return;
  }

  try {
    setError("");
    setSuccessMessage("");

    const data = await apiRequest(
      `/api/issues/${issueId}/assignments`,
      {
        method: "POST",
        body: JSON.stringify({
          assignedTo: assignedTo,
          note: "Issue assigned from Manage Issues.",
        }),
      }
    );

    setIssues((previousIssues) =>
      previousIssues.map((issue) =>
        issue.id === issueId
          ? {
              ...issue,
              status: data.issue.status,
              updated_at: data.issue.updated_at,
            }
          : issue
      )
    );

    setSuccessMessage("Issue assigned successfully.");

    setSelectedAssignees((previousSelections) => ({
      ...previousSelections,
      [issueId]: "",
    }));
  } catch (error) {
    console.error("Failed to assign issue:", error.message);
    setError(error.message);
  }
};

const issueCounts = {
  reported: issues.filter((issue) => issue.status === "reported").length,
  under_review: issues.filter((issue) => issue.status === "under_review").length,
  assigned: issues.filter((issue) => issue.status === "assigned").length,
  in_progress: issues.filter((issue) => issue.status === "in_progress").length,
  resolved: issues.filter((issue) => issue.status === "resolved").length,
  rejected: issues.filter((issue) => issue.status === "rejected").length,
};

const priorityCounts = {
  low: issues.filter((issue) => issue.priority === "low").length,
  medium: issues.filter((issue) => issue.priority === "medium").length,
  high: issues.filter((issue) => issue.priority === "high").length,
  critical: issues.filter((issue) => issue.priority === "critical").length,
};

const filteredIssues = issues
  .filter((issue) => {
    const matchesStatus =
      statusFilter === "all" || issue.status === statusFilter;

    const matchesPriority =
      priorityFilter === "all" || issue.priority === priorityFilter;

    const matchesSearch =
      issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (issue.address || "").toLowerCase().includes(searchTerm.toLowerCase());

    return matchesStatus && matchesPriority && matchesSearch;
  })
  .sort((a, b) => {
    if (sortOption === "newest") {
      return new Date(b.created_at) - new Date(a.created_at);
    }

    if (sortOption === "oldest") {
      return new Date(a.created_at) - new Date(b.created_at);
    }

    if (sortOption === "recently_updated") {
      return new Date(b.updated_at) - new Date(a.updated_at);
    }

    return 0;
  });

  return (
    <div className="manage-issues-page">
      <Navbar />

      <h1>Manage Issues</h1>

      <div className="issue-controls">
  <label htmlFor="issue-search">
    <strong>Search Issues:</strong>{" "}
  </label>

  <input
    id="issue-search"
    type="text"
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    placeholder="Search by title..."
  />

      <div className="filter-control">
  <label htmlFor="status-filter">
    <strong>Filter by Status:</strong>{" "}
  </label>

  <select
    id="status-filter"
    value={statusFilter}
    onChange={(e) => setStatusFilter(e.target.value)}
  >
    <option value="all">All</option>
    <option value="reported">Reported</option>
    <option value="under_review">Under Review</option>
    <option value="assigned">Assigned</option>
    <option value="in_progress">In Progress</option>
    <option value="resolved">Resolved</option>
    <option value="rejected">Rejected</option>
  </select>
</div>

<div className="filter-control">
  <label htmlFor="priority-filter">
    <strong>Filter by Priority:</strong>{" "}
  </label>

  <select
    id="priority-filter"
    value={priorityFilter}
    onChange={(e) => setPriorityFilter(e.target.value)}
  >
    <option value="all">All</option>
    <option value="low">Low</option>
    <option value="medium">Medium</option>
    <option value="high">High</option>
    <option value="critical">Critical</option>
  </select>
</div>


<div className="filter-control">
  <label htmlFor="sort-option">
    <strong>Sort By:</strong>{" "}
  </label>

  <select
    id="sort-option"
    value={sortOption}
    onChange={(e) => setSortOption(e.target.value)}
  >
    <option value="newest">Newest First</option>
    <option value="oldest">Oldest First</option>
    <option value="recently_updated">Recently Updated</option>
  </select>
</div>

<button
  type="button"
  onClick={() => {
    setSearchTerm("");
    setStatusFilter("all");
    setPriorityFilter("all");
    setSortOption("newest");
  }}
>
  Clear Filters
</button>
</div>

      {loading && <p>Loading issues...</p>}

      {error && <p>{error}</p>}
      {successMessage && <p>{successMessage}</p>}

      {!loading && !error && (
  <div>
    <p className="total-issues">
  Total Issues: {issues.length}
</p>

    <div className="issue-summary">
  <h2>Issue Summary</h2>

  <div className="issue-summary-list">
  <p className="summary-card">
    Reported: {issueCounts.reported}
  </p>

  <p className="summary-card">
    Under Review: {issueCounts.under_review}
  </p>

  <p className="summary-card">
    Assigned: {issueCounts.assigned}
  </p>

  <p className="summary-card">
    In Progress: {issueCounts.in_progress}
  </p>

  <p className="summary-card">
    Resolved: {issueCounts.resolved}
  </p>

  <p className="summary-card">
    Rejected: {issueCounts.rejected}
  </p>
</div>
</div>

<div className="priority-summary">
  <h2>Priority Summary</h2>

  <div className="priority-summary-list">
    <p className="summary-card">
      Low: {priorityCounts.low}
    </p>

    <p className="summary-card">
      Medium: {priorityCounts.medium}
    </p>

    <p className="summary-card">
      High: {priorityCounts.high}
    </p>

    <p className="summary-card">
      Critical: {priorityCounts.critical}
    </p>
  </div>
</div>

    <div className="issues-list-header">
  <h2>All Issues</h2>
  <p>
    Showing {filteredIssues.length} of {issues.length} issues
  </p>
</div>

    {filteredIssues.length === 0 ? (
      <p>No issues found.</p>
    ) : (
      <div>
        {filteredIssues.map((issue) => (
  <div className="issue-card" key={issue.id}>
            <h2 className="issue-card-title">
  <Link to={`/issues/${issue.id}`}>{issue.title}</Link>
</h2>
            <p>
              <strong>Category:</strong> {issue.category}
            </p>

            <p>
  <strong>Status:</strong> {formatStatus(issue.status)}
</p>

            <div className="issue-action">
  <label htmlFor={`status-${issue.id}`}>
    <strong>Update Status:</strong>{" "}
  </label>

  <select
  id={`status-${issue.id}`}
  value={issue.status}
  disabled={updatingIssueId === issue.id}
  onChange={(e) =>
    handleStatusUpdate(issue.id, e.target.value)
  }
>
  <option value={issue.status}>
    {formatStatus(issue.status)}
  </option>

  {getNextStatuses(issue.status).map((status) => (
    <option key={status} value={status}>
      {formatStatus(status)}
    </option>
  ))}
</select>

  {updatingIssueId === issue.id && <span> Updating...</span>}
</div>

{issue.status === "under_review" && (
  <div className="issue-action">
    <label htmlFor={`assignee-${issue.id}`}>
      <strong>Assign To:</strong>{" "}
    </label>

    <select
      id={`assignee-${issue.id}`}
      value={selectedAssignees[issue.id] || ""}
      onChange={(e) =>
        setSelectedAssignees((previousSelections) => ({
          ...previousSelections,
          [issue.id]: e.target.value,
        }))
      }
    >
      <option value="">Select authority/admin</option>

      {assignableUsers.map((user) => (
        <option key={user.id} value={user.id}>
          {user.name} ({user.role})
        </option>
      ))}
    </select>

    <button
      type="button"
      onClick={() => handleAssignment(issue.id)}
    >
      Assign Issue
    </button>
  </div>
)}

            <p>
              <strong>Priority:</strong> {issue.priority}
            </p>

            <p>
              <strong>Address:</strong>{" "}
              {issue.address || "Not provided"}
            </p>

            <p>
              <strong>Reported:</strong>{" "}
              {new Date(issue.created_at).toLocaleString()}
            </p>

          </div>
        ))}
      </div>
    )}
  </div>
)}
    </div>
  );
}

export default ManageIssues;