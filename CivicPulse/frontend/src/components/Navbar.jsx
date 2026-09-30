import { useContext } from "react";
import { Link } from "react-router-dom";
import AuthContext from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useContext(AuthContext);

  return (
    <nav>
      <h2>CivicPulse</h2>

      {user && (
        <div>
  <Link to="/dashboard">Dashboard</Link>
  {" | "}

  {user.role === "citizen" && (
    <Link to="/report-issue">Report an Issue</Link>
  )}

  {user.role === "authority" && (
    <Link to="/manage-issues">Manage Issues</Link>
  )}

  {user.role === "admin" && (
    <Link to="/manage-issues">Manage Issues</Link>
  )}

  {" | "}
  <span>Welcome, {user.name}</span>
  {" "}
  <button onClick={logout}>Logout</button>
</div>
      )}
    </nav>
  );
}

export default Navbar;