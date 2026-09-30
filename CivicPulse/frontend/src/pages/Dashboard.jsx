import { useContext, useEffect, useState } from "react";
import AuthContext from "../context/AuthContext";
import Navbar from "../components/Navbar";
import { apiRequest } from "../services/api";
import IssueCard from "../components/IssueCard";

function Dashboard() {
  const { user } = useContext(AuthContext);

  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMyIssues = async () => {
      try {
        const data = await apiRequest("/api/issues/my");

        setIssues(data.issues);
      } catch (error) {
        console.error("Failed to fetch issues:", error.message);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMyIssues();
  }, []);

  return (
    <div>
      <Navbar />

      <h1>CivicPulse Dashboard</h1>

      {user && (
        <div>
          <h2>Welcome, {user.name}</h2>
          <p>Email: {user.email}</p>
          <p>Role: {user.role}</p>
        </div>
      )}

      <hr />

      <h2>My Reported Issues</h2>

      {loading && <p>Loading your issues...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && issues.length === 0 && (
        <p>You have not reported any issues yet.</p>
      )}

      {!loading && !error && issues.length > 0 && (
  <div>
    {issues.map((issue) => (
      <IssueCard key={issue.id} issue={issue} />
    ))}
  </div>
)}
  
    </div>
  );
}

export default Dashboard;