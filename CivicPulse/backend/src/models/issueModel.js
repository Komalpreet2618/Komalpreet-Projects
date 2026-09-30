const pool = require("../config/db");

const createIssue = async (
  title,
  description,
  category,
  priority,
  latitude,
  longitude,
  address,
  reportedBy
) => {
  const query = `
    INSERT INTO issues (
      title,
      description,
      category,
      priority,
      location,
      address,
      reported_by
    )
    VALUES (
      $1,
      $2,
      $3,
      $4,
      ST_SetSRID(ST_MakePoint($6, $5), 4326)::geography,
      $7,
      $8
    )
    RETURNING
  id,
  title,
  description,
  category,
  status,
  priority,
  ST_Y(location::geometry) AS latitude,
  ST_X(location::geometry) AS longitude,
  address,
  reported_by,
  created_at,
  updated_at;
  `;

  const values = [
    title,
    description,
    category,
    priority,
    latitude,
    longitude,
    address,
    reportedBy,
  ];

  const result = await pool.query(query, values);

  return result.rows[0];
};

const getAllIssues = async () => {
  const query = `
    SELECT
      id,
      title,
      description,
      category,
      status,
      priority,
      ST_Y(location::geometry) AS latitude,
      ST_X(location::geometry) AS longitude,
      address,
      reported_by,
      created_at,
      updated_at
    FROM issues
    ORDER BY created_at DESC;
  `;

  const result = await pool.query(query);

  return result.rows;
};

const getIssuesByUser = async (userId) => {
  const query = `
    SELECT
      id,
      title,
      description,
      category,
      status,
      priority,
      ST_Y(location::geometry) AS latitude,
      ST_X(location::geometry) AS longitude,
      address,
      reported_by,
      created_at,
      updated_at
    FROM issues
    WHERE reported_by = $1
    ORDER BY created_at DESC;
  `;

  const result = await pool.query(query, [userId]);

  return result.rows;
};

const getIssueById = async (id) => {
  const query = `
    SELECT
      id,
      title,
      description,
      category,
      status,
      priority,
      ST_Y(location::geometry) AS latitude,
      ST_X(location::geometry) AS longitude,
      address,
      reported_by,
      created_at,
      updated_at
    FROM issues
    WHERE id = $1;
  `;

  const result = await pool.query(query, [id]);

  return result.rows[0];
};

const updateIssueStatus = async (id, status) => {
  const query = `
    UPDATE issues
    SET
      status = $2,
      updated_at = CURRENT_TIMESTAMP
    WHERE id = $1
    RETURNING
      id,
      title,
      description,
      category,
      status,
      priority,
      ST_Y(location::geometry) AS latitude,
      ST_X(location::geometry) AS longitude,
      address,
      reported_by,
      created_at,
      updated_at;
  `;

  const result = await pool.query(query, [id, status]);

  return result.rows[0];
};

const updateIssueStatusWithClient = async (client, id, status) => {
  const query = `
    UPDATE issues
    SET
      status = $2,
      updated_at = CURRENT_TIMESTAMP
    WHERE id = $1
    RETURNING
      id,
      title,
      description,
      category,
      status,
      priority,
      ST_Y(location::geometry) AS latitude,
      ST_X(location::geometry) AS longitude,
      address,
      reported_by,
      created_at,
      updated_at;
  `;

  const result = await client.query(query, [id, status]);

  return result.rows[0];
};

module.exports = {
  createIssue,
  getAllIssues,
  getIssuesByUser,
  getIssueById,
  updateIssueStatus,
  updateIssueStatusWithClient,
};