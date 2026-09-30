const pool = require("../config/db");

const findUserByEmail = async (email) => {
  const result = await pool.query(
    "SELECT * FROM users WHERE email = $1",
    [email]
  );

  return result.rows[0];
};

const findUserById = async (userId) => {
  const result = await pool.query(
    "SELECT id, name, email, role FROM users WHERE id = $1",
    [userId]
  );

  return result.rows[0];
};

const getAssignableUsers = async () => {
  const result = await pool.query(
    `SELECT id, name, email, role
     FROM users
     WHERE role IN ('authority', 'admin')
     ORDER BY name ASC`
  );

  return result.rows;
};

const createUser = async (name, email, passwordHash, role = "citizen") => {
  const result = await pool.query(
    `INSERT INTO users (name, email, password_hash, role)
     VALUES ($1, $2, $3, $4)
     RETURNING id, name, email, role, created_at, updated_at`,
    [name, email, passwordHash, role]
  );

  return result.rows[0];
};

module.exports = {
  findUserByEmail,
  findUserById,
  getAssignableUsers,
  createUser,
};