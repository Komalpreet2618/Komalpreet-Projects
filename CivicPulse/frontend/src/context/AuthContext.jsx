import { createContext, useEffect, useState } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      return;
    }

    const restoreUser = async () => {
  try {
    const response = await fetch("http://localhost:5000/api/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to restore user");
    }

    const data = await response.json();
    setUser(data.user);
  } catch (error) {
    console.error("Failed to restore user:", error.message);
    localStorage.removeItem("token");
    setUser(null);
  } finally {
    setLoading(false);
  }
};

    restoreUser();
  }, []);

  const logout = () => {
  localStorage.removeItem("token");
  setUser(null);
};

return (
  <AuthContext.Provider value={{ user, setUser, logout, loading }}>
    {children}
  </AuthContext.Provider>
);
}

export default AuthContext;