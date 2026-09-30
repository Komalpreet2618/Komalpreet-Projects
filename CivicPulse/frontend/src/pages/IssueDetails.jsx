import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import { apiRequest } from "../services/api";

function IssueDetails() {
  const { id } = useParams();

  const [issue, setIssue] = useState(null);
  const [history, setHistory] = useState([]);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [images, setImages] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchIssue = async () => {
      try {
        const data = await apiRequest(`/api/issues/${id}`);
        setIssue(data.issue);

        const historyData = await apiRequest(`/api/issues/${id}/history`);
        setHistory(historyData.history);

        const imageData = await apiRequest(`/api/issues/${id}/images`);
        setImages(imageData.images);

        const commentData = await apiRequest(`/api/issues/${id}/comments`);
        setComments(commentData.comments);

        const assignmentData = await apiRequest(
  `/api/issues/${id}/assignments`
);
setAssignments(assignmentData.assignments);

      } catch (error) {
        console.error("Failed to fetch issue:", error.message);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchIssue();
  }, [id]);

  const handleAddComment = async () => {
  if (!commentText.trim()) {
    return;
  }

  try {
    const data = await apiRequest(`/api/issues/${id}/comments`, {
      method: "POST",
      body: JSON.stringify({
        comment: commentText.trim(),
      }),
    });

    setComments((previousComments) => [
      ...previousComments,
      data.comment,
    ]);

    setCommentText("");
  } catch (error) {
    console.error("Failed to add comment:", error.message);
    setError(error.message);
  }
};

  return (
    <div>
      <Navbar />

      <h1>Issue Details</h1>

      <Link to="/dashboard">← Back to Dashboard</Link>

      {loading && <p>Loading issue...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && issue && (
        <div>
          <h2>{issue.title}</h2>

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
            <strong>Address:</strong>{" "}
            {issue.address || "Not provided"}
          </p>

          <p>
            <strong>Latitude:</strong> {issue.latitude}
          </p>

          
          <p><strong>Longitude:</strong> {issue.longitude}</p>

          <h2>Issue Images</h2>

          {images.length === 0 ? (
          <p>No images uploaded.</p>
          ) : (
          <div>
            {images.map((image) => (
          <div key={image.id}>
            <img
              src={`http://localhost:5000${image.image_url}`}
              alt="Civic issue"
              width="300"
          />
          </div>
    ))}
  </div>
)}

<h2>Issue History</h2>

      {history.length === 0 ? (
        <p>No status updates yet.</p>
) : (
  <div>
    {history.map((update) => (
      <div key={update.id}>
        <p>
          <strong>
            {update.previous_status} → {update.new_status}
          </strong>
        </p>

        {update.comment && <p>Comment: {update.comment}</p>}

        <p>
          Updated by: {update.updated_by_name} ({update.updated_by_role})
        </p>

        <p>
          Date: {new Date(update.created_at).toLocaleString()}
        </p>

        <hr />
      </div>
    ))}
  </div>
)}

<h2>Assignments</h2>

{assignments.length === 0 ? (
  <p>No assignments yet.</p>
) : (
  <div>
    {assignments.map((assignment) => (
      <div key={assignment.id}>
        <p>
          <strong>Assigned To:</strong>{" "}
          {assignment.assigned_to_name} ({assignment.assigned_to_role})
        </p>

        <p>
          <strong>Assigned By:</strong>{" "}
          {assignment.assigned_by_name} ({assignment.assigned_by_role})
        </p>

        <p>
          <strong>Date:</strong>{" "}
          {new Date(assignment.assigned_at).toLocaleString()}
        </p>

        {assignment.note && (
          <p>
            <strong>Note:</strong> {assignment.note}
          </p>
        )}

        <hr />
      </div>
    ))}
  </div>
)}

<h2>Comments</h2>

{comments.length === 0 ? (
  <p>No comments yet.</p>
) : (
  <div>
    {comments.map((comment) => (
      <div key={comment.id}>
        <p>
          <strong>{comment.commented_by_name}</strong>
          {" "}
          ({comment.commented_by_role})
        </p>

        <p>{comment.comment}</p>

        <p>
          Date: {new Date(comment.created_at).toLocaleString()}
        </p>

        <hr />
      </div>
    ))}
  </div>
)}

<div>
  <h3>Add a Comment</h3>

  <textarea
    value={commentText}
    onChange={(e) => setCommentText(e.target.value)}
    placeholder="Write your comment..."
    rows="4"
  />

  <button type="button" onClick={handleAddComment}>
  Submit Comment
</button>
</div>

        </div>
      )}
    </div>
  );
}

export default IssueDetails;