import { Link } from "react-router-dom";

function IssueCard({ issue }) {
  return (
    <div>
      <h3>{issue.title}</h3>

      <p>{issue.description}</p>

      <p>
        <strong>Category:</strong> {issue.category}
      </p>

      <p>
        <strong>Status:</strong> {issue.status}
      </p>

      <p>
        <strong>Priority:</strong> {issue.priority}
      </p>

      <p>
        <strong>Address:</strong> {issue.address || "Not provided"}
      </p>

      <Link to={`/issues/${issue.id}`}>View Details</Link>

      <hr />
    </div>
  );
}

export default IssueCard;